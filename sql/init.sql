-- init.sql

-- 创建 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建合并后的表
CREATE TABLE image_data (
    id SERIAL,
    image_id UUID NOT NULL,
    s3_url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    timestamp TIMESTAMPTZ NOT NULL,
    location TEXT NOT NULL,
    vector vector(1280) NOT NULL, -- MobileNet V3 Large 输出 1280 维向量
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 创建分区
CREATE TABLE image_data_2024 PARTITION OF image_data
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 创建索引
CREATE INDEX idx_image_id ON image_data (image_id);
CREATE INDEX idx_status ON image_data (status);
CREATE INDEX idx_timestamp ON image_data (timestamp);
CREATE INDEX idx_location ON image_data (location);
CREATE INDEX idx_vector ON image_data USING ivfflat (vector vector_l2_ops);

-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建更新时间戳的触发器
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON image_data
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- 创建通知插入的触发器函数
CREATE OR REPLACE FUNCTION notify_image_data_insert()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('image_data_insert', json_build_object('image_id', NEW.image_id)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建通知插入的触发器
CREATE TRIGGER image_data_insert_trigger
AFTER INSERT ON image_data
FOR EACH ROW
EXECUTE FUNCTION notify_image_data_insert();

-- 创建函数来确保 timestamp 和 created_at 一致
CREATE OR REPLACE FUNCTION set_consistent_timestamps()
RETURNS TRIGGER AS $$
BEGIN
    NEW.timestamp = CURRENT_TIMESTAMP;
    NEW.created_at = NEW.timestamp;
    NEW.updated_at = NEW.timestamp;
    RETURN NEW;
end;
$$ LANGUAGE plpgsql;

-- 创建触发器来应用一致的时间戳
CREATE TRIGGER ensure_consistent_timestamps
BEFORE INSERT ON image_data
FOR EACH ROW
EXECUTE FUNCTION set_consistent_timestamps();