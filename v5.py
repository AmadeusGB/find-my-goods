import os
import base64
import requests
import argparse

# 从环境变量中读取 API 密钥
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

PHOTOS_API_URL = "http://localhost:5001/api/photos"
PHOTOS_DIR = 'photos'

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

# Function to get GPT-4 visual response
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
            "max_tokens": 1200
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        message = result['choices'][0]['message']['content']
        return message.strip()
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ask a question to GPT-4 visual model.')
    parser.add_argument('--question', type=str, required=True, help='The question to ask about the images.')
    parser.add_argument('--count', type=int, default=5, help='The number of recent photos to fetch from the API.')
    args = parser.parse_args()

    recent_photos = get_recent_photos(PHOTOS_API_URL, args.count)
    image_paths = [os.path.join(PHOTOS_DIR, photo) for photo in recent_photos]
    result = gpt4_visual_test(image_paths, args.question)
    print("GPT-4 Visual Response:", result)
