import os
import uuid
import json
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

PHOTOS_DIR = os.getenv('PHOTOS_DIR', 'photos')
DATABASE_URL = os.getenv('DATABASE_URL', 'dbname=pgdatabase user=pguser password=pgpassword host=localhost')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

class PhotoList(BaseModel):
    photos: List[str]

class UploadResponse(BaseModel):
    message: str
    filename: str

@app.get("/api/ping")
async def ping_pong():
    return JSONResponse(content={"message": "pong"})

@app.get("/api/photos", response_model=PhotoList)
async def list_photos(count: int = 5):
    try:
        photos = [f for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
        photos.sort(key=lambda x: os.path.getmtime(os.path.join(PHOTOS_DIR, x)), reverse=True)
        recent_photos = photos[:count]
        return {"photos": recent_photos}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Photos directory not found")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_photo(
    file: UploadFile = File(...),
    location: str = Form(...),
    timestamp: str = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    if file and location and timestamp:
        filename = file.filename
        save_path = os.path.join(PHOTOS_DIR, filename)
        
        with open(save_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        image_id = str(uuid.uuid4())
        zero_vector = [0.0] * 1536

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO image_queue (image_id, s3_url, status, timestamp, location)
                    VALUES (%s, %s, 'pending', %s, %s)
                """, (image_id, save_path, timestamp, location))

                cursor.execute("""
                    INSERT INTO image_metadata (image_id, description, vector)
                    VALUES (%s, %s, %s)
                """, (image_id, '{}', json.dumps(zero_vector)))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()

        return {"message": "File uploaded and queued successfully", "filename": filename}
    
    raise HTTPException(status_code=400, detail="Missing required parameters")

if __name__ == '__main__':
    import uvicorn
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
    uvicorn.run(app, host="0.0.0.0", port=5001)