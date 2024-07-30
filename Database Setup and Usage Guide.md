# Database Setup and Usage Guide

## Introduction

This document provides a comprehensive guide for setting up and using the PostgreSQL database for our project. The database is designed to store and manage image data, including metadata and vectorized representations for efficient similarity matching. We use the `pgvector` extension to handle vector data types.

## Table of Contents

1. [Overview](#overview)
   - [Database Tables](#database-tables)
   - [Key Features](#key-features)
2. [Prerequisites](#prerequisites)
   - [Software Requirements](#software-requirements)
3. [Database Setup](#database-setup)
   - [Step 1: Install PostgreSQL and Extensions](#step-1-install-postgresql-and-extensions)
   - [Step 2: Create the Database and Tables](#step-2-create-the-database-and-tables)
4. [Data Management](#data-management)
   - [Inserting Data](#inserting-data)
   - [Querying Data](#querying-data)
   - [Updating Data](#updating-data)
   - [Deleting Data](#deleting-data)
5. [Example Queries](#example-queries)
6. [Maintenance and Optimization](#maintenance-and-optimization)
7. [Appendix](#appendix)
   - [SQL Scripts](#sql-scripts)

## Overview

### Database Tables

Our database consists of two main tables:

1. **image_queue**: This table functions as a queue system to handle image processing tasks.
2. **image_metadata**: This table stores detailed metadata about images, including a vectorized representation for similarity matching.

### Key Features

- Efficient storage and management of image metadata.
- Vectorized image data for similarity searches using the `pgvector` extension.
- Triggers and indexes to ensure data integrity and optimize query performance.

## Prerequisites

### Software Requirements

- PostgreSQL (version 12 or higher)
- `pgvector` extension for PostgreSQL
- Basic knowledge of SQL and PostgreSQL

## Database Setup

### Step 1: Install PostgreSQL and Extensions

1. **Install PostgreSQL**: Follow the instructions on the [PostgreSQL official site](https://www.postgresql.org/download/) to install PostgreSQL on your system.

2. **Install `pgvector` Extension**: Use Homebrew on macOS or the package manager for your OS to install `pgvector`:
   ```bash
   brew install pgvector
   ```

3. **Set Environment Variables**:
   ```bash
   export PGUSER=pguser
   export PGPASSWORD=pgpassword
   export PGDATABASE=pgdatabase
   export PGSSLMODE=disable
   ```

4. **Connect to PostgreSQL as Superuser**:
   ```bash
   psql -h localhost -U postgres
   ```

5. **Create the `pgvector` Extension**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Step 2: Create the Database and Tables

1. **Create and Initialize the Database**:
   ```bash
   createdb $PGDATABASE
   ```

2. **Run the SQL Script to Create Tables**:
   ```bash
   psql -h localhost -d $PGDATABASE -U $PGUSER -f init.sql
   ```

## Data Management

### Inserting Data

To insert a new image into the `image_queue` table:
```sql
INSERT INTO image_queue (image_id, s3_url, status, timestamp, location) VALUES ('uuid', 's3_url', 'pending', 'timestamp', 'location');
```

### Querying Data

To query all pending images:
```sql
SELECT * FROM image_queue WHERE status = 'pending';
```

### Updating Data

To update the status of an image:
```sql
UPDATE image_queue SET status = 'processed' WHERE image_id = 'uuid';
```

### Deleting Data

To delete an image record:
```sql
DELETE FROM image_queue WHERE image_id = 'uuid';
```

## Example Queries

1. **Retrieve all images captured in a specific location**:
   ```sql
   SELECT * FROM image_queue WHERE location = 'bedroom';
   ```

2. **Find images with a specific metadata description**:
   ```sql
   SELECT * FROM image_metadata WHERE description @> '{"MainEntities": [{"Object": "person"}]}';
   ```

3. **Search for similar images using vectors**:
   ```sql
   SELECT * FROM image_metadata ORDER BY vector <-> '[vector_representation]' LIMIT 5;
   ```

## Maintenance and Optimization

1. **Regularly analyze and vacuum tables** to maintain performance:
   ```sql
   VACUUM ANALYZE image_queue;
   VACUUM ANALYZE image_metadata;
   ```

2. **Monitor index usage** and rebuild if necessary:
   ```sql
   REINDEX TABLE image_queue;
   REINDEX TABLE image_metadata;
   ```

## Appendix

### SQL Scripts

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

By following this guide, you will be able to set up and manage your PostgreSQL database efficiently, ensuring optimal performance for storing and querying image metadata and vector representations.