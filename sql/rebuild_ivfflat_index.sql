-- 删除旧索引
DROP INDEX IF EXISTS idx_vector_metadata;

-- 重新创建索引
CREATE INDEX idx_vector_metadata ON image_metadata USING ivfflat (vector vector_l2_ops) WITH (lists = 100);

-- 注意：'lists' 参数可能需要根据您的数据量和分布进行调整