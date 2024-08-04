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
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')
PHOTOS_API_URL = "http://localhost:5001/api/photos"
PHOTOS_DIR = 'photos'

app = FastAPI()

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

class ImageMetadata(BaseModel):
    description: Optional[str] = None
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
    zero_vector = [0.0] * 1536

    # Convert timestamp string to UTC datetime object
    try:
        timestamp_dt = datetime.fromisoformat(timestamp)
        if timestamp_dt.tzinfo is None:
            timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)
        else:
            timestamp_dt = timestamp_dt.astimezone(timezone.utc)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format. Expected ISO format.")

    async with app.state.db_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("""
                INSERT INTO image_queue (image_id, s3_url, status, timestamp, location)
                VALUES ($1, $2, 'pending', $3, $4)
            """, image_id, save_path, timestamp_dt, location)

            await conn.execute("""
                INSERT INTO image_metadata (image_id, description, vector)
                VALUES ($1, $2, $3)
            """, image_id, '{}', json.dumps(zero_vector))

    return {"message": "File uploaded and queued successfully", "filename": filename}

@app.get("/api/image_metadata/{image_id}", response_model=ImageMetadata)
async def get_image_metadata(
    image_id: str,
    include_description: bool = Query(True, description="Include description in the response"),
    include_vector: bool = Query(False, description="Include vector in the response")
):
    select_parts = []
    if include_description:
        select_parts.append("description")
    if include_vector:
        select_parts.append("vector")
    
    if not select_parts:
        raise HTTPException(status_code=400, detail="At least one of description or vector must be requested")
    
    query = f"SELECT {', '.join(select_parts)} FROM image_metadata WHERE image_id = $1"

    async with app.state.db_pool.acquire() as conn:
        result = await conn.fetchrow(query, image_id)

        if not result:
            raise HTTPException(status_code=404, detail="Image metadata not found")

        response = ImageMetadata()
        if include_description and 'description' in result:
            response.description = result['description']
        if include_vector and 'vector' in result:
            response.vector = json.loads(result['vector'])

        return response

@lru_cache(maxsize=1000)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_recent_photos(count):
    photos = [f for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
    photos.sort(key=lambda x: os.path.getmtime(os.path.join(PHOTOS_DIR, x)), reverse=True)
    return photos[:count]

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

@app.post("/api/ask")
async def ask_gpt4_visual(request: QuestionRequest):
    try:
        recent_photos = get_recent_photos(request.count)
        image_paths = [os.path.join(PHOTOS_DIR, photo) for photo in recent_photos]
        return StreamingResponse(gpt4_visual_test(image_paths, request.question), media_type="text/event-stream")
    except Exception as e:
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
                return data["data"][0]["embedding"]
    except Exception as e:
        print(f"Error in vectorize_text: {e}")
        return []


async def handle_notification(conn, pid, channel, payload):
    try:
        payload_data = json.loads(payload)
        image_id = payload_data.get('image_id')

        image_data = await conn.fetchrow(
            "SELECT s3_url, timestamp, location FROM image_queue WHERE image_id = $1",
            image_id
        )
        if not image_data:
            return

        s3_url = image_data['s3_url']
        timestamp = image_data['timestamp']
        location = image_data['location']

        with open("image_to_text_prompt.txt", "r") as file:
            prompt = file.read().strip()

        description = await describe_image(s3_url, prompt)

        # Ensure the timestamp is in UTC (it should already be, but let's be sure)
        timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        # Format the timestamp in ISO format with 'Z' indicating UTC
        formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        print(f"Formatted timestamp: {formatted_timestamp}")

        description = description.replace('unique_image_id', s3_url)
        description = description.replace('YYYY-MM-DDTHH:MM:SS', formatted_timestamp)
        description = description.replace('home', location)
        
        vector = await vectorize_text(description)

        async with conn.transaction():
            await conn.execute("""
                UPDATE image_metadata
                SET description = $1, vector = $2
                WHERE image_id = $3
            """, description, json.dumps(vector), image_id)

            await conn.execute("""
                UPDATE image_queue
                SET status = 'completed'
                WHERE image_id = $1
            """, image_id)
    except Exception as e:
        print(f"Error handling notification: {e}")

@app.on_event("startup")
async def startup():
    async def listen_to_notifications():
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.add_listener('image_queue_insert', handle_notification)
        while True:
            await asyncio.sleep(3600)  # Keep the connection alive

    asyncio.create_task(listen_to_notifications())

if __name__ == "__main__":
    import uvicorn
    
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)