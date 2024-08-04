-- 检查数据量
SELECT COUNT(*) FROM image_metadata;

-- 检查索引大小
SELECT pg_size_pretty(pg_relation_size('idx_vector_metadata'));

-- 执行一个示例查询并检查执行时间
EXPLAIN ANALYZE SELECT * FROM image_metadata 
ORDER BY vector <-> (SELECT vector FROM image_metadata LIMIT 1)
LIMIT 10;