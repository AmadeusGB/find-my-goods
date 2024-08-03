import requests
import os

def upload_image(image_path, location, timestamp, server_url='http://127.0.0.1:8000/api/upload'):
    with open(image_path, 'rb') as img_file:
        files = {'file': (os.path.basename(image_path), img_file)}
        data = {'location': location, 'timestamp': timestamp}
        response = requests.post(server_url, files=files, data=data)
        if response.status_code == 200:
            print(f"Image {image_path} uploaded successfully.")
        else:
            print(f"Failed to upload image {image_path}. Status code: {response.status_code}")