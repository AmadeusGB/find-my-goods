from flask import Flask, jsonify
import os

app = Flask(__name__)
PHOTOS_DIR = 'photos'

@app.route('/api/photos', methods=['GET'])
def list_photos():
    try:
        photos = [os.path.join(PHOTOS_DIR, f) for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
        # 按文件修改时间排序
        photos.sort(key=os.path.getmtime, reverse=True)
        # 只取最近的10张照片
        recent_photos = photos[:10]
        # 返回文件名列表，而不是完整路径
        recent_photos = [os.path.basename(photo) for photo in recent_photos]
        return jsonify({'photos': recent_photos})
    except FileNotFoundError:
        return jsonify({'error': 'Photos directory not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
