# 数据库设置和使用指南

## 介绍

本文档提供了一个全面的指南，用于设置和使用我们的项目的 PostgreSQL 数据库。该数据库设计用于存储和管理图像数据，包括元数据和向量化表示，以实现高效的相似性匹配。我们使用 `pgvector` 扩展来处理向量数据类型。

## 目录

1. [概述](#概述)
   - [数据库表](#数据库表)
   - [关键功能](#关键功能)
2. [先决条件](#先决条件)
   - [软件要求](#软件要求)
3. [数据库设置](#数据库设置)
   - [步骤1：安装 PostgreSQL 和扩展](#步骤1安装-postgresql-和扩展)
   - [步骤2：创建数据库和表](#步骤2创建数据库和表)
4. [数据管理](#数据管理)
   - [插入数据](#插入数据)
   - [查询数据](#查询数据)
   - [更新数据](#更新数据)
   - [删除数据](#删除数据)
5. [示例查询](#示例查询)
6. [维护和优化](#维护和优化)
7. [附录](#附录)
   - [SQL 脚本](#sql-脚本)

## 概述

### 数据库表

我们的数据库包含两个主要表：

1. **image_queue**：该表用作处理图像任务的队列系统。
2. **image_metadata**：该表存储有关图像的详细元数据，包括用于相似性匹配的向量化表示。

### 关键功能

- 高效的图像元数据存储和管理。
- 使用 `pgvector` 扩展进行的向量化图像数据处理，以实现相似性搜索。
- 触发器和索引确保数据完整性并优化查询性能。

## 先决条件

### 软件要求

- PostgreSQL（版本12或更高）
- PostgreSQL 的 `pgvector` 扩展
- 基本的 SQL 和 PostgreSQL 知识

## 数据库设置

### 步骤1：安装 PostgreSQL 和扩展

1. **安装 PostgreSQL**：按照 [PostgreSQL 官方网站](https://www.postgresql.org/download/) 上的说明在您的系统上安装 PostgreSQL。

2. **安装 `pgvector` 扩展**：在 macOS 上使用 Homebrew 或者使用您的操作系统的包管理器来安装 `pgvector`：
   ```bash
   brew install pgvector
   ```

3. **设置环境变量**：
   ```bash
   export PGUSER=pguser
   export PGPASSWORD=pgpassword
   export PGDATABASE=pgdatabase
   export PGSSLMODE=disable
   ```

4. **以超级用户身份连接到 PostgreSQL**：
   ```bash
   psql -h localhost -U postgres
   ```

5. **创建 `pgvector` 扩展**：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 步骤2：创建数据库和表

1. **创建并初始化数据库**：
   ```bash
   createdb $PGDATABASE
   ```

2. **运行 SQL 脚本以创建表**：
   ```bash
   psql -h localhost -d $PGDATABASE -U $PGUSER -f init.sql
   ```

## 数据管理

### 插入数据

要将新图像插入 `image_queue` 表：
```sql
INSERT INTO image_queue (image_id, s3_url, status, timestamp, location) VALUES ('uuid', 's3_url', 'pending', 'timestamp', 'location');
```

### 查询数据

要查询所有待处理的图像：
```sql
SELECT * FROM image_queue WHERE status = 'pending';
```

### 更新数据

要更新图像的状态：
```sql
UPDATE image_queue SET status = 'processed' WHERE image_id = 'uuid';
```

### 删除数据

要删除图像记录：
```sql
DELETE FROM image_queue WHERE image_id = 'uuid';
```

## 示例查询

1. **检索在特定位置捕获的所有图像**：
   ```sql
   SELECT * FROM image_queue WHERE location = 'bedroom';
   ```

2. **查找具有特定元数据描述的图像**：
   ```sql
   SELECT * FROM image_metadata WHERE description @> '{"MainEntities": [{"Object": "person"}]}';
   ```

3. **使用向量搜索相似图像**：
   ```sql
   SELECT * FROM image_metadata ORDER BY vector <-> '[vector_representation]' LIMIT 5;
   ```

## 维护和优化

1. **定期分析和真空表** 以维护性能：
   ```sql
   VACUUM ANALYZE image_queue;
   VACUUM ANALYZE image_metadata;
   ```

2. **监控索引使用情况** 并在必要时重建索引：
   ```sql
   REINDEX TABLE image_queue;
   REINDEX TABLE image_metadata;
   ```

## 附录

### SQL 脚本

#### init.sql

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS image_queue (
    id SERIAL PRIMARY KEY,
    image_id UUID NOT NULL,
    s3_url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    timestamp TIMESTAMPTZ NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_image_id UNIQUE (image_id)
);

CREATE INDEX idx_image_id_queue ON image_queue (image_id);
CREATE INDEX idx_location_queue ON image_queue (location);
CREATE INDEX idx_status_queue ON image_queue (status);
CREATE INDEX idx_timestamp_queue ON image_queue (timestamp);

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

CREATE TABLE IF NOT EXISTS image_metadata (
    id SERIAL PRIMARY KEY,
    image_id UUID NOT NULL,
    description JSONB NOT NULL,
    vector VECTOR(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_image_metadata UNIQUE (image_id)
);

CREATE INDEX idx_image_id_metadata ON image_metadata (image_id);
CREATE INDEX idx_vector_metadata ON image_metadata USING ivfflat (vector);
```

---

通过遵循本指南，您将能够高效地设置和管理您的 PostgreSQL 数据库，确保图像元数据和向量表示的最佳性能。