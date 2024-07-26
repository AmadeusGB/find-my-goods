import os
import base64
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中读取 API 密钥
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

PHOTOS_API_URL = "http://localhost:5001/api/photos"
PHOTOS_DIR = 'photos'

app = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gpt_client.v6:app", host="127.0.0.1", port=8000, reload=True)
