-- init.sql

-- 创建 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建分区表
CREATE TABLE image_queue (
    id SERIAL,
    image_id UUID NOT NULL,
    s3_url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    timestamp TIMESTAMPTZ NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 创建分区
CREATE TABLE image_queue_2024 PARTITION OF image_queue
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 创建索引
CREATE INDEX idx_image_id_queue ON image_queue (image_id);
CREATE INDEX idx_status_queue ON image_queue (status);
CREATE INDEX idx_timestamp_queue ON image_queue (timestamp);
CREATE INDEX idx_location_queue ON image_queue (location);

-- 创建触发器
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON image_queue
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- 创建 image_metadata 表
CREATE TABLE image_metadata (
    id SERIAL PRIMARY KEY,
    image_id UUID NOT NULL,
    description TEXT NOT NULL,
    vector vector(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(image_id)
);

CREATE INDEX idx_image_id_metadata ON image_metadata (image_id);
CREATE INDEX idx_vector_metadata ON image_metadata USING ivfflat (vector);

-- 创建触发器函数
CREATE OR REPLACE FUNCTION notify_image_queue_insert()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('image_queue_insert', json_build_object('image_id', NEW.image_id)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER image_queue_insert_trigger
AFTER INSERT ON image_queue
FOR EACH ROW
EXECUTE FUNCTION notify_image_queue_insert();
