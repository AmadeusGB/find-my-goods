from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)
PHOTOS_DIR = 'photos'
DESCRIBE_API_URL = 'http://127.0.0.1:8000/describe'

@app.route('/api/photos', methods=['GET'])
def list_photos():
    try:
        photos = [os.path.join(PHOTOS_DIR, f) for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
        # 按文件修改时间排序
        photos.sort(key=os.path.getmtime, reverse=True)

        # 获取查询参数 count，默认为 5
        count = int(request.args.get('count', 5))

        # 只取最近的 count 张照片
        recent_photos = photos[:count]
        # 返回文件名列表，而不是完整路径
        recent_photos = [os.path.basename(photo) for photo in recent_photos]
        return jsonify({'photos': recent_photos})
    except FileNotFoundError:
        return jsonify({'error': 'Photos directory not found'}), 404

@app.route('/api/upload', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        save_path = os.path.join(PHOTOS_DIR, filename)
        file.save(save_path)
        
        # 调用 /describe 接口
        describe_response = requests.post(
            DESCRIBE_API_URL,
            json={'filename': filename}
        )
        
        if describe_response.status_code != 200:
            return jsonify({'message': 'File uploaded but description failed', 'filename': filename}), 200
        
        description = describe_response.json().get('description')
        return jsonify({'message': 'File uploaded successfully', 'filename': filename, 'description': description}), 200

if __name__ == '__main__':
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
    app.run(host='0.0.0.0', port=5001)
