import os
import base64
import requests

# 从环境变量中读取 API 密钥
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get GPT-4 visual response
def gpt4_visual_test(image_paths):
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
                            "text": "红色的袋子在哪里?"
                        },
                        *images
                    ]
                }
            ],
            "max_tokens": 600
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        message = result['choices'][0]['message']['content']
        return message.strip()
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    image_paths = [
        "photos/living_room_iphone_motion_photo_2.jpg",
        "photos/living_room_iphone_motion_photo_3.jpg",
        "photos/living_room_iphone_motion_photo_4.jpg"
    ]
    result = gpt4_visual_test(image_paths)
    print("GPT-4 Visual Response:", result)
