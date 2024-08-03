import os
import base64
import json
import uuid
from typing import List, Optional
from functools import lru_cache

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')
PHOTOS_API_URL = "http://localhost:5001/api/photos"
PHOTOS_DIR = 'photos'

app = FastAPI()

# Function to get a new database connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Dependency to get a database connection
async def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

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
    timestamp: str = Form(...),
    db: psycopg2.extensions.connection = Depends(get_db)
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

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO image_queue (image_id, s3_url, status, timestamp, location)
                VALUES (%s, %s, 'pending', %s, %s)
            """, (image_id, save_path, timestamp, location))

            cursor.execute("""
                INSERT INTO image_metadata (image_id, description, vector)
                VALUES (%s, %s, %s)
            """, (image_id, '{}', json.dumps(zero_vector)))

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": "File uploaded and queued successfully", "filename": filename}

@app.get("/api/image_metadata/{image_id}", response_model=ImageMetadata)
async def get_image_metadata(
    image_id: str,
    include_description: bool = Query(True, description="Include description in the response"),
    include_vector: bool = Query(False, description="Include vector in the response"),
    db: psycopg2.extensions.connection = Depends(get_db)
):
    select_parts = []
    if include_description:
        select_parts.append("description")
    if include_vector:
        select_parts.append("vector")
    
    if not select_parts:
        raise HTTPException(status_code=400, detail="At least one of description or vector must be requested")
    
    query = f"SELECT {', '.join(select_parts)} FROM image_metadata WHERE image_id = %s"

    try:
        with db.cursor() as cursor:
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Image metadata not found")

            response = ImageMetadata()
            if include_description and 'description' in result:
                response.description = result['description']
            if include_vector and 'vector' in result:
                response.vector = json.loads(result['vector'])

            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@lru_cache(maxsize=1000)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_recent_photos(count):
    photos = [f for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
    photos.sort(key=lambda x: os.path.getmtime(os.path.join(PHOTOS_DIR, x)), reverse=True)
    return photos[:count]

def gpt4_visual_test(image_paths, question):
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
            "model": "gpt-4o",
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

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, stream=True)
        response.raise_for_status()

        return StreamingResponse(response.iter_content(chunk_size=1024), media_type="text/event-stream")
    except Exception as e:
        return StreamingResponse(iter([f"An error occurred: {e}"]), media_type="text/event-stream")

@app.get("/api/ping")
async def ping_pong():
    return JSONResponse(content={"message": "pong"})

@app.post("/api/ask")
async def ask_gpt4_visual(request: QuestionRequest):
    try:
        recent_photos = get_recent_photos(request.count)
        image_paths = [os.path.join(PHOTOS_DIR, photo) for photo in recent_photos]
        return gpt4_visual_test(image_paths, request.question)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def describe_image(image_path, prompt):
    try:
        encoded_image = encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        payload = {
            "model": "gpt-4o",
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

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

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

def vectorize_text(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }

    response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def handle_notification(notification):
    conn = get_db_connection()
    try:
        payload = json.loads(notification.payload)
        image_id = payload.get('image_id')

        with conn.cursor() as cursor:
            cursor.execute("SELECT s3_url, timestamp, location FROM image_queue WHERE image_id = %s", (image_id,))
            image_data = cursor.fetchone()
            if not image_data:
                return

            s3_url = image_data['s3_url']
            timestamp = image_data['timestamp']
            location = image_data['location']

            with open("image_to_text_prompt.txt", "r") as file:
                prompt = file.read().strip()

            description = describe_image(s3_url, prompt)

            description = description.replace('unique_image_id', s3_url)
            description = description.replace('YYYY-MM-DDTHH:MM:SS', timestamp.strftime('%Y-%m-%dT%H:%M:%S'))
            description = description.replace('home', location)
            
            vector = vectorize_text(description)

            cursor.execute("""
                UPDATE image_metadata
                SET description = %s, vector = %s
                WHERE image_id = %s
            """, (description, json.dumps(vector), image_id))

            cursor.execute("""
                UPDATE image_queue
                SET status = 'completed'
                WHERE image_id = %s
            """, (image_id,))

            conn.commit()
    except Exception as e:
        print(f"Error handling notification: {e}")
        conn.rollback()
    finally:
        conn.close()

@app.on_event("startup")
async def startup():
    def listen_to_notifications():
        print("Listening for notifications on channel 'image_queue_insert'...")
        conn = get_db_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            with conn.cursor() as cursor:
                cursor.execute("LISTEN image_queue_insert;")
                while True:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        handle_notification(notify)
        finally:
            conn.close()

    import threading
    listener_thread = threading.Thread(target=listen_to_notifications)
    listener_thread.daemon = True
    listener_thread.start()

if __name__ == "__main__":
    import uvicorn
    
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)