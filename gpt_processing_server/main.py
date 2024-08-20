import os
import base64
import json
import uuid
import asyncio
from typing import List, Optional
from functools import lru_cache
from datetime import datetime, timezone

import aiohttp
import asyncpg
import logging
import torch
import clip
from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langdetect import detect, LangDetectException, DetectorFactory

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')
PHOTOS_DIR = 'photos'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

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
    max_images: int = 5
    
class DescribeImageRequest(BaseModel):
    filename: str

# Language detection setup
DetectorFactory.seed = 0

@lru_cache(maxsize=1000)
def _detect_language_sync(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"  # Default to English if detection fails

async def detect_language(text: str) -> str:
    sample = text[:100]
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _detect_language_sync, sample)

@lru_cache(maxsize=1000)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
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
    zero_vector = [0.0] * 512  # CLIP uses 512-dimensional vectors

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

def format_timestamp(timestamp: datetime) -> str:
    """
    Format the timestamp to 'YYYY-MM-DD HH:MM:SS' in UTC.
    
    :param timestamp: datetime object
    :return: formatted string
    """
    # Ensure the timestamp is in UTC
    utc_timestamp = timestamp.astimezone(timezone.utc)
    return utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")

async def gpt4_visual_speak(image_metadata, question, language):
    try:
        sorted_metadata = sorted(image_metadata, key=lambda x: x['timestamp'])
        
        messages = []
        for index, data in enumerate(sorted_metadata):
            encoded_image = await asyncio.to_thread(encode_image, data['s3_url'])
            messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            })
            formatted_timestamp = format_timestamp(data['timestamp'])
            messages.append({
                "type": "text",
                "text": f"Image {index + 1} details:\nTimestamp: {formatted_timestamp} UTC\nLocation: {data['location']}"
            })

        detailed_prompt = f"""
        Analyze the following {len(sorted_metadata)} images of kitchen scenes and describe the activities and changes occurring over time. Each image is accompanied by its timestamp (in UTC) and location. Follow these enhanced guidelines:

        1. Use the provided timestamps to organize your response, e.g., "**[Timestamp UTC] - [Location]:**".

        2. Provide highly detailed descriptions using the 5W1H method (Who, When, What, Where, Why, How):
           - Describe people's appearances, actions, and possible emotions.
           - Note specific objects, their positions, and any changes.
           - Speculate on the reasons behind activities and changes you observe.

        3. Use a conversational and engaging tone, as if you're telling a story to a friend. Include:
           - Vivid language and sensory details (e.g., "The aroma of freshly brewed coffee filled the air").
           - Gentle humor or lighthearted observations where appropriate.
           - Empathetic insights into the people's actions or situations.

        4. Make educated guesses about activities between visible time periods to create a more cohesive narrative.

        5. Focus on the most interesting aspects of kitchen life, including:
           - Family dynamics and interactions.
           - Cooking processes and meal preparations.
           - Changes in the kitchen's state (e.g., from messy to clean or vice versa).

        6. Relate your observations directly to the user's question: "{question}"

        7. Start your description immediately without any introductory statements.

        8. Provide your response in the {language} language, adapting your style to sound natural in that language.

        Remember, the goal is to paint a vivid, engaging picture of daily life in this kitchen, making the scenes come alive for the reader while accurately referencing the provided timestamps (in UTC) and locations.
        """

        messages.append({
            "type": "text",
            "text": detailed_prompt
        })

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": messages
                }
            ],
            "max_tokens": 1800,
            "stream": True
        }

        timeout = aiohttp.ClientTimeout(total=150)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        yield line
    except asyncio.TimeoutError:
        yield "Error: Request timed out".encode()
    except Exception as e:
        yield f"An error occurred: {str(e)}".encode()
        
@app.get("/api/ping")
async def ping_pong():
    return JSONResponse(content={"message": "pong"})

async def get_relevant_photos(question: str, max_images: int, db_pool):
    question_vector = await vectorize_text(question)
    
    if not question_vector:
        raise HTTPException(status_code=500, detail="Failed to vectorize the question")
    
    async with db_pool.acquire() as conn:
        similar_images = await conn.fetch("""
            SELECT s3_url, timestamp, location, vector <-> $1 AS distance
            FROM image_data
            WHERE status = 'completed'
            ORDER BY distance
            LIMIT $2
        """, json.dumps(question_vector), max_images)
        
        if not similar_images:
            logging.info(f"No relevant images found!")
            return []
        
        return [{'s3_url': img['s3_url'], 'timestamp': img['timestamp'], 'location': img['location']} for img in similar_images]
    
@app.post("/api/ask")
async def ask_gpt4_visual_search(request: QuestionRequest):
    try:
        max_images = max(1, min(request.max_images, 5))
        relevant_photos = await get_relevant_photos(request.question, max_images, app.state.db_pool)
        
        if not relevant_photos:
            return JSONResponse(content={"message": "No relevant photos found"})
        
        language = await detect_language(request.question)
        
        logging.info(f"Selected images for question '{request.question}': {relevant_photos}")
        
        return StreamingResponse(gpt4_visual_speak(relevant_photos, request.question, language), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"Error in ask_gpt4_visual_search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

async def vectorize_text(text):
    try:
        with torch.no_grad():
            text_inputs = clip.tokenize([text]).to(device)
            text_features = model.encode_text(text_inputs)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            return text_features.cpu().numpy()[0].tolist()
    except Exception as e:
        logging.error(f"Error in vectorize_text: {e}")
        return []

async def vectorize_image(image_path):
    try:
        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            return image_features.cpu().numpy()[0].tolist()
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