TRUNCATE TABLE image_metadata RESTART IDENTITY CASCADE;
TRUNCATE TABLE image_queue RESTART IDENTITY CASCADE;
TRUNCATE TABLE image_queue_2024 RESTART IDENTITY CASCADE;
TRUNCATE TABLE stuck_record_log RESTART IDENTITY CASCADE;


ALTER SEQUENCE image_metadata_id_seq RESTART WITH 1;
ALTER SEQUENCE image_queue_id_seq RESTART WITH 1;
ALTER SEQUENCE stuck_record_log_id_seq RESTART WITH 1;


SELECT * FROM image_queue;

SELECT * FROM image_metadata;


DROP TABLE IF EXISTS image_queue CASCADE;
DROP TABLE IF EXISTS image_metadata CASCADE;
DROP TABLE IF EXISTS stuck_record_log CASCADE;
DROP FUNCTION IF EXISTS update_timestamp CASCADE;
DROP FUNCTION IF EXISTS notify_image_queue_insert CASCADE;
DROP FUNCTION IF EXISTS set_consistent_timestamps CASCADE;
DROP FUNCTION IF EXISTS handle_stuck_pending_records CASCADE;
DROP FUNCTION IF EXISTS reset_failed_record CASCADE;


psql -h localhost -U pguser -d pgdatabase


python3.9 camera_client/main.py --device 1 --mode photo --interval 60 --duration 600 --threshold 60 --min_contour_area 4000 --detection_interval 1 --location bedroom --image_format jpg

uvicorn gpt_processing_server.v9:app --host 127.0.0.1 --port 8000 --reload

cd workspaces/find-my-goods

curl -X GET "http://localhost:8000/api/image_metadata/60ca9b4b-f3f8-4422-b5e2-66508501ee6d?include_description=true&include_vector=false"

curl -X GET "http://localhost:8000/api/image_metadata/60ca9b4b-f3f8-4422-b5e2-66508501ee6d?include_description=true&include_vector=true"

curl -X POST http://localhost:8000/api/ask1 \
     -H "Content-Type: application/json" \
     -d '{"question": "我的眼镜在哪里?", "count": 5}'

python main.py "粉红色袋子在哪里?"

python main.py "粉红色袋子在哪里?" --count 10