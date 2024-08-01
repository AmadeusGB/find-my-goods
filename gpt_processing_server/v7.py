import os
import base64
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')
PHOTOS_API_URL = "http://localhost:5001/api/photos"
PHOTOS_DIR = 'photos'

app = FastAPI()

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

CONNECTION = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
CONNECTION.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get recent photos from API
def get_recent_photos(api_url, count):
    try:
        response = requests.get(api_url, params={'count': count})
        response.raise_for_status()
        data = response.json()
        return data.get('photos', [])
    except Exception as e:
        print(f"An error occurred while fetching recent photos: {e}")
        return []

# Function to get GPT-4 visual response and stream it directly to the client
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
            "Authorization": f"Bearer {api_key}"
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

        return StreamingResponse(response.raw, media_type="text/event-stream")
    except Exception as e:
        return StreamingResponse(iter([f"An error occurred: {e}"]), media_type="text/event-stream")

class QuestionRequest(BaseModel):
    question: str
    count: int = 5

@app.post("/ask")
async def ask_gpt4_visual(request: QuestionRequest):
    try:
        recent_photos = get_recent_photos(PHOTOS_API_URL, request.count)
        image_paths = [os.path.join(PHOTOS_DIR, photo) for photo in recent_photos]
        return gpt4_visual_test(image_paths, request.question)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# New function to describe a single image
def describe_image(image_path, prompt):
    try:
        encoded_image = encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
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

class DescribeImageRequest(BaseModel):
    filename: str

@app.post("/describe")
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
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }

    response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def handle_notification(notification):
    payload = json.loads(notification.payload)
    image_id = payload.get('image_id')

    with CONNECTION.cursor() as cursor:
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

        # 更新描述信息中的字段
        description = description.replace('unique_image_id', s3_url)
        description = description.replace('YYYY-MM-DDTHH:MM:SS', timestamp.strftime('%Y-%m-%dT%H:%M:%S'))
        description = description.replace('home', location)
        
        # 使用 GPT-4 Embeddings 将描述进行向量化
        vector = vectorize_text(description)

        # 更新 image_metadata 表
        cursor.execute("""
            UPDATE image_metadata
            SET description = %s, vector = %s
            WHERE image_id = %s
        """, (description, vector, image_id))

        # 更新 image_queue 表状态为 "completed"
        cursor.execute("""
            UPDATE image_queue
            SET status = 'completed'
            WHERE image_id = %s
        """, (image_id,))

        CONNECTION.commit()

@app.on_event("startup")
async def startup():
    def listen_to_notifications():
        print("Listening for notifications on channel 'image_queue_insert'...")
        with CONNECTION.cursor() as cursor:
            cursor.execute("LISTEN image_queue_insert;")
            while True:
                CONNECTION.poll()
                while CONNECTION.notifies:
                    notify = CONNECTION.notifies.pop(0)
                    handle_notification(notify)

    import threading
    listener_thread = threading.Thread(target=listen_to_notifications)
    listener_thread.daemon = True
    listener_thread.start()

if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    # 启动监听通知的线程
    notification_thread = Thread(target=listen_notifications, daemon=True)
    notification_thread.start()

    # 启动 FastAPI 服务器
    uvicorn.run("gpt_processing_server.v7:app", host="127.0.0.1", port=8000, reload=True)
