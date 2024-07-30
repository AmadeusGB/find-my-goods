from flask import Flask, jsonify, request
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
import uuid
import json

load_dotenv()

app = Flask(__name__)

PHOTOS_DIR = os.getenv('PHOTOS_DIR', 'photos')
DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')
CONNECTION = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/api/photos', methods=['GET'])
def list_photos():
    try:
        photos = [os.path.join(PHOTOS_DIR, f) for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
        photos.sort(key=os.path.getmtime, reverse=True)

        count = int(request.args.get('count', 5))
        recent_photos = photos[:count]
        recent_photos = [os.path.basename(photo) for photo in recent_photos]
        return jsonify({'photos': recent_photos})
    except FileNotFoundError:
        return jsonify({'error': 'Photos directory not found'}), 404

@app.route('/api/upload', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    location = request.form.get('location')
    timestamp = request.form.get('timestamp')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and location and timestamp:
        filename = file.filename
        save_path = os.path.join(PHOTOS_DIR, filename)
        file.save(save_path)

        image_id = uuid.uuid4()

        zero_vector = [0.0] * 768

        with CONNECTION.cursor() as cursor:
            cursor.execute("""
                INSERT INTO image_queue (image_id, s3_url, status, timestamp, location)
                VALUES (%s, %s, 'pending', %s, %s)
            """, (str(image_id), save_path, timestamp, location))
            
            cursor.execute("""
                INSERT INTO image_metadata (image_id, description, vector)
                VALUES (%s, '{}', %s)
            """, (str(image_id), json.dumps(zero_vector)))
            
            CONNECTION.commit()

        return jsonify({'message': 'File uploaded and queued successfully', 'filename': filename}), 200

    return jsonify({'error': 'Missing required parameters'}), 400

if __name__ == '__main__':
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
    app.run(host='0.0.0.0', port=5001)
