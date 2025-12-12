## Phase 2: Quick Start Guide

### 1. Start PostgreSQL (30 seconds)

```bash
cd /workspaces/lool-/data-collection
docker-compose -f config/docker-compose.postgres.yml up -d
```

**Verify it's running:**
```bash
docker ps | grep legal_rag_postgres
```

---

### 2. Run All Migrations (1 minute)

```bash
./migrations/run_all_migrations.sh
```

**Expected output:**
```
✓ PostgreSQL is running
✓ Database exists
[1/9] Running 001_create_core_tables.sql...
✓ 001_create_core_tables.sql completed
...
✓ All migrations completed successfully!
```

---

### 3. Test Database Connection (Python)

```python
from src.database import DatabaseConnection, Document

# Connect and test
with DatabaseConnection() as db:
    # Health check
    health = db.health_check()
    print(f"Status: {health['status']}")
    print(f"Database Size: {health['database_size']}")

    # Query documents
    with db.session_scope() as session:
        count = session.query(Document).count()
        print(f"Total Documents: {count}")
```

---

### 4. Generate Sample Data (Optional)

```bash
psql -h localhost -p 5433 -U legal_rag_user -d legal_rag_db -c "SELECT generate_sample_documents(10);"
```

---

### 5. Access PgAdmin (Optional)

Open browser: http://localhost:5050

**Login:**
- Email: `admin@legalrag.local`
- Password: `admin_password_2024`

**Connect to database:**
- Host: `postgres` (inside Docker network) or `host.docker.internal`
- Port: `5432` (internal) or `5433` (external)
- Database: `legal_rag_db`
- User: `legal_rag_user`
- Password: `secure_rag_password_2024`

---

### 6. Useful Database Queries

**Check table sizes:**
```sql
SELECT * FROM get_database_stats();
```

**Health check:**
```sql
SELECT * FROM health_check();
```

**View recent documents:**
```sql
SELECT global_id, title_full, doc_type, doc_year
FROM documents
ORDER BY created_at DESC
LIMIT 10;
```

**Check sequence status:**
```sql
SELECT * FROM sequence_tracker;
```

**View scraping sources:**
```sql
SELECT source_name, country_code, is_active, priority
FROM scrape_sources
WHERE is_active = TRUE
ORDER BY priority DESC;
```

---

### 7. Stop PostgreSQL

```bash
docker-compose -f config/docker-compose.postgres.yml down
```

**Stop and remove data:**
```bash
docker-compose -f config/docker-compose.postgres.yml down -v
```

---

### Troubleshooting

**PostgreSQL won't start:**
```bash
# Check logs
docker-compose -f config/docker-compose.postgres.yml logs postgres

# Restart
docker-compose -f config/docker-compose.postgres.yml restart
```

**Migration fails:**
```bash
# Run individual migration manually
psql -h localhost -p 5433 -U legal_rag_user -d legal_rag_db -f migrations/001_create_core_tables.sql
```

**Connection refused:**
- Check if PostgreSQL is running: `docker ps`
- Check port 5433 is not in use: `lsof -i :5433`
- Try connecting manually: `psql -h localhost -p 5433 -U legal_rag_user -d legal_rag_db`

---

### What's Next?

✅ **Phase 2 Complete** - Database ready!

**Phase 3**: Metadata Extraction
- PDF text extraction
- Citation parsing
- Subject classification
- Quality scoring

**Phase 4**: Scraper Integration
- Update scrapers to use new database
- Multi-tier storage implementation
- Chunking pipeline
