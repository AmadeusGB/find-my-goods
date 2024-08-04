# SQL Scripts for Database Management

This directory contains SQL scripts for initializing and maintaining the database for the Find My Goods project.

## Files

1. `init.sql`: Initializes the database schema, including tables, indexes, and functions.
2. `check_index_performance.sql`: Checks the performance of the IVFFlat index.
3. `rebuild_ivfflat_index.sql`: Rebuilds the IVFFlat index for optimized performance.

## Usage

### Initializing the Database

To initialize the database, run:

```bash
psql -h localhost -d your_database -U your_username -f sql/init.sql
```

Replace `your_database` and `your_username` with your actual database name and username.

### Checking Index Performance

To check the performance of the IVFFlat index, run:

```bash
psql -h localhost -d your_database -U your_username -f sql/check_index_performance.sql
```

Run this script periodically, especially after significant data growth, to monitor index performance.

### Rebuilding the IVFFlat Index

If the index performance degrades or after significant data growth, rebuild the index:

```bash
psql -h localhost -d your_database -U your_username -f sql/rebuild_ivfflat_index.sql
```

## Guidelines

1. **Initial Setup**: Always run `init.sql` first when setting up a new database.

2. **Regular Maintenance**: 
   - Run `check_index_performance.sql` regularly, especially after adding a large amount of new data.
   - Monitor the query execution time and index size reported by this script.

3. **Index Optimization**:
   - If you notice a significant slowdown in query performance or if the data size has increased substantially (e.g., 10x growth), consider rebuilding the index.
   - Use `rebuild_ivfflat_index.sql` to rebuild the index. You may need to adjust the `lists` parameter in this script based on your data size and distribution.

4. **Data Volume Considerations**:
   - The IVFFlat index performs better with larger datasets. The initial warning about "low recall" is normal for small datasets.
   - As your data grows, the index performance should improve naturally.

5. **Performance Tuning**:
   - If you're experiencing performance issues even after rebuilding the index, consider consulting a database performance expert.
   - You may need to adjust other database parameters or optimize your queries further.

6. **Backup**: Always backup your database before running any maintenance scripts, especially before rebuilding indexes.

## Note

These scripts are designed for the PostgreSQL database with the pgvector extension. Ensure that your database setup matches these requirements before running the scripts.

For any issues or further customization needs, please consult the project's technical lead or a database administrator.