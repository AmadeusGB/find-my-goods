from flask import Flask, jsonify
import os

app = Flask(__name__)
PHOTOS_DIR = 'photos'

@app.route('/api/photos', methods=['GET'])
def list_photos():
    try:
        photos = os.listdir(PHOTOS_DIR)
        return jsonify({'photos': photos})
    except FileNotFoundError:
        return jsonify({'error': 'Photos directory not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
