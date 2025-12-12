#!/bin/bash
# Run all PostgreSQL migrations for Legal RAG System
# Usage: ./run_all_migrations.sh [database_url]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database connection (from environment or parameter)
DB_URL="${1:-postgresql://legal_rag_user:secure_rag_password_2024@localhost:5433/legal_rag_db}"

# Parse connection string
DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DB_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

echo -e "${YELLOW}==================================================================${NC}"
echo -e "${YELLOW}  Legal RAG System - Database Migration Runner${NC}"
echo -e "${YELLOW}==================================================================${NC}"
echo ""
echo -e "Database: ${GREEN}$DB_NAME${NC}"
echo -e "Host: ${GREEN}$DB_HOST:$DB_PORT${NC}"
echo -e "User: ${GREEN}$DB_USER${NC}"
echo ""

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
if ! PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot connect to PostgreSQL at $DB_HOST:$DB_PORT${NC}"
    echo -e "${YELLOW}Make sure PostgreSQL is running:${NC}"
    echo -e "  docker-compose -f config/docker-compose.postgres.yml up -d"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"
echo ""

# Check if database exists, create if not
echo -e "${YELLOW}Checking database '$DB_NAME'...${NC}"
if ! PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}Creating database '$DB_NAME'...${NC}"
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
    echo -e "${GREEN}✓ Database created${NC}"
else
    echo -e "${GREEN}✓ Database exists${NC}"
fi
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Migration files
MIGRATIONS=(
    "001_create_core_tables.sql"
    "002_create_content_tables.sql"
    "003_create_reference_tables.sql"
    "004_create_metadata_tables.sql"
    "005_create_rag_tables.sql"
    "006_create_system_tables.sql"
    "007_create_scraping_tables.sql"
    "008_create_indexes.sql"
    "009_seed_data.sql"
)

# Run migrations
echo -e "${YELLOW}==================================================================${NC}"
echo -e "${YELLOW}  Running Migrations${NC}"
echo -e "${YELLOW}==================================================================${NC}"
echo ""

TOTAL=${#MIGRATIONS[@]}
CURRENT=0

for migration in "${MIGRATIONS[@]}"; do
    CURRENT=$((CURRENT + 1))
    echo -e "${YELLOW}[$CURRENT/$TOTAL] Running $migration...${NC}"

    if PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$SCRIPT_DIR/$migration" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $migration completed${NC}"
    else
        echo -e "${RED}✗ $migration failed${NC}"
        echo -e "${RED}Running with output for debugging:${NC}"
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$SCRIPT_DIR/$migration"
        exit 1
    fi
    echo ""
done

# Summary
echo -e "${YELLOW}==================================================================${NC}"
echo -e "${YELLOW}  Migration Summary${NC}"
echo -e "${YELLOW}==================================================================${NC}"
echo ""
echo -e "${GREEN}✓ All migrations completed successfully!${NC}"
echo ""

# Show database statistics
echo -e "${YELLOW}Database Statistics:${NC}"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT * FROM get_database_stats();" 2>/dev/null || true
echo ""

# Show health check
echo -e "${YELLOW}Health Check:${NC}"
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT * FROM health_check();" 2>/dev/null || true
echo ""

echo -e "${GREEN}==================================================================${NC}"
echo -e "${GREEN}  Database is ready for use!${NC}"
echo -e "${GREEN}==================================================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Test connection: PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo -e "  2. Generate sample data: SELECT generate_sample_documents(10);"
echo -e "  3. View statistics: SELECT * FROM get_database_stats();"
echo ""
