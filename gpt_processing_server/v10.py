import os
import base64
import json
import uuid
import asyncio
import numpy as np
from typing import List, Optional
from functools import lru_cache
from datetime import datetime, timezone

import aiohttp
import asyncpg
import logging
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')
PHOTOS_DIR = 'photos'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Load MobileNet V3 Large model
model = mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.DEFAULT)
model.classifier = torch.nn.Sequential(
    model.classifier[0],
    torch.nn.Linear(1280, 1280)
)
model.eval()

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Use asyncpg for asynchronous database operations
async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@app.on_event("startup")
async def startup_event():
    app.state.db_pool = await get_db_pool()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.db_pool.close()

class UploadResponse(BaseModel):
    message: str
    filename: str

class ImageVector(BaseModel):
    vector: Optional[List[float]] = None

class QuestionRequest(BaseModel):
    question: str
    count: int = 5
    
class DescribeImageRequest(BaseModel):
    filename: str

@app.post("/api/upload", response_model=UploadResponse)
async def upload_photo(
    file: UploadFile = File(...),
    location: str = Form(...),
    timestamp: str = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    filename = file.filename
    save_path = os.path.join(PHOTOS_DIR, filename)
    
    content = await file.read()
    with open(save_path, "wb") as buffer:
        buffer.write(content)

    image_id = str(uuid.uuid4())
    zero_vector = [0.0] * 1280

    # Convert timestamp string to UTC datetime object
    try:
        timestamp_dt = datetime.fromisoformat(timestamp)
        if timestamp_dt.tzinfo is None:
            timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)
        else:
            timestamp_dt = timestamp_dt.astimezone(timezone.utc)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Expected ISO format.")

    # Use the current time for both timestamp and created_at
    current_time = datetime.now(timezone.utc)
    
    async with app.state.db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO image_data (image_id, s3_url, status, timestamp, location, vector, created_at)
            VALUES ($1, $2, 'pending', $3, $4, $5, $3)
        """, image_id, save_path, current_time, location, json.dumps(zero_vector))

    return {"message": "File uploaded and queued successfully", "filename": filename}

@app.get("/api/image_vector/{image_id}", response_model=ImageVector)
async def get_image_vector(image_id: str):
    async with app.state.db_pool.acquire() as conn:
        result = await conn.fetchrow("SELECT vector FROM image_data WHERE image_id = $1", image_id)

        if not result:
            raise HTTPException(status_code=404, detail="Image vector not found")

        return ImageVector(vector=json.loads(result['vector']))

@lru_cache(maxsize=1000)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def gpt4_visual_test(image_paths, question):
    try:
        images = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
                }
            }
            for image_path in image_paths
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        *images
                    ]
                }
            ],
            "max_tokens": 1200,
            "stream": True
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        yield line
    except Exception as e:
        yield f"An error occurred: {str(e)}".encode()

@app.get("/api/ping")
async def ping_pong():
    return JSONResponse(content={"message": "pong"})

async def get_relevant_photos(question: str, count: int, db_pool):
    question_vector = await vectorize_text(question)
    
    if not question_vector:
        raise HTTPException(status_code=500, detail="Failed to vectorize the question")
    
    async with db_pool.acquire() as conn:
        similar_images = await conn.fetch("""
            SELECT image_id, s3_url, vector <-> $1 AS distance
            FROM image_data
            WHERE status = 'completed'
            ORDER BY distance
            LIMIT $2
        """, json.dumps(question_vector), count)
        
        if not similar_images:
            return []
        
        return [{'image_id': img['image_id'], 's3_url': img['s3_url']} for img in similar_images]
    
@app.post("/api/ask")
async def ask_gpt4_visual_search(request: QuestionRequest):
    try:
        relevant_photos = await get_relevant_photos(request.question, request.count, app.state.db_pool)
        if not relevant_photos:
            return JSONResponse(content={"message": "No relevant photos found"})
        
        # Extract s3_urls from relevant_photos
        image_paths = [photo['s3_url'] for photo in relevant_photos]
        
        # Log the selected image paths
        logging.info(f"Selected images for question '{request.question}': {image_paths}")
        
        return StreamingResponse(gpt4_visual_test(image_paths, request.question), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"Error in ask_gpt4_visual_search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    
async def describe_image(image_path, prompt):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1200
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in describe_image: {e}")
        return str(e)

@app.post("/api/describe")
async def describe_image_endpoint(request: DescribeImageRequest):
    try:
        image_path = os.path.join(PHOTOS_DIR, request.filename)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")

        with open("image_to_text_prompt.txt", "r") as file:
            prompt = file.read().strip()
        
        description = describe_image(image_path, prompt)
        print(description)  # Print the description to the console
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def vectorize_text(text):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "text-embedding-3-small",
            "input": text
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                vector_1536 = np.array(data["data"][0]["embedding"])
            
        vector_1280 = np.dot(vector_1536, np.random.randn(1536, 1280))
        
        vector_1280 = vector_1280 / np.linalg.norm(vector_1280)
        
        return vector_1280.tolist()
    except Exception as e:
        print(f"Error in vectorize_text: {e}")
        return []

async def vectorize_image(image_path):
    try:
        image = Image.open(image_path).convert('RGB')
        input_tensor = preprocess(image).unsqueeze(0)
        with torch.no_grad():
            vector = model(input_tensor).squeeze().tolist()
        
        if len(vector) != 1280:
            raise ValueError(f"Expected 1280 dimensions, got {len(vector)}")
        
        return vector
    except Exception as e:
        logging.error(f"Error in vectorize_image: {e}")
        return []
    
async def handle_notification(conn, pid, channel, payload):
    try:
        logging.info(f"Received notification: {payload}")
        payload_data = json.loads(payload)
        image_id = payload_data.get('image_id')

        logging.info(f"Processing image_id: {image_id}")

        image_data = await conn.fetchrow(
            "SELECT s3_url FROM image_data WHERE image_id = $1",
            image_id
        )
        if not image_data:
            logging.warning(f"No image data found for image_id: {image_id}")
            return

        s3_url = image_data['s3_url']
        logging.info(f"Vectorizing image: {s3_url}")

        vector = await vectorize_image(s3_url)

        if not vector:
            logging.error(f"Failed to vectorize image: {s3_url}")
            return

        logging.info(f"Updating database with vector for image_id: {image_id}")
        async with conn.transaction():
            await conn.execute("""
                UPDATE image_data
                SET vector = $1, status = 'completed'
                WHERE image_id = $2
            """, json.dumps(vector), image_id)
            
        logging.info(f"Image processed successfully for image_id: {image_id}, s3_url: {s3_url}")
    except Exception as e:
        logging.error(f"Error handling notification for image_id: {image_id}: {str(e)}")

@app.on_event("startup")
async def startup():
    async def listen_to_notifications():
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.add_listener('image_data_insert', handle_notification)
        logging.info("Started listening for image_data_insert notifications")
        while True:
            await asyncio.sleep(3600)   # Keep the connection alive

    asyncio.create_task(listen_to_notifications())

if __name__ == "__main__":
    import uvicorn
    
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)