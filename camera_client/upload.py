# camera_client/upload.py

import requests
import os

def upload_image(image_path, server_url):
    with open(image_path, 'rb') as img_file:
        files = {'file': img_file}
        response = requests.post(server_url, files=files)
        if response.status_code == 200:
            print(f"Image {image_path} uploaded successfully.")
        else:
            print(f"Failed to upload image {image_path}. Status code: {response.status_code}")
