import requests
import os
import logging
from requests.exceptions import RequestException

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_image(image_path, location, timestamp, server_url='http://127.0.0.1:8000/api/upload'):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, 'rb') as img_file:
            files = {'file': (os.path.basename(image_path), img_file)}
            data = {'location': location, 'timestamp': timestamp}
            
            response = requests.post(server_url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                logging.info(f"Image {image_path} uploaded successfully.")
            else:
                logging.error(f"Failed to upload image {image_path}. Status code: {response.status_code}")
                return False

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        return False
    except RequestException as e:
        logging.error(f"Request error during upload of {image_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during upload of {image_path}: {e}")
        return False

    return True