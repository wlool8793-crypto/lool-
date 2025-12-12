#!/bin/bash
# ============================================================================
# PostgreSQL Setup Script for Phase 4
# Installs and configures PostgreSQL for high-performance legal data collection
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="indiankanoon"
DB_USER="indiankanoon_user"
DB_PASSWORD="secure_pass_2024"
DB_PORT="5432"
POSTGRES_VERSION="15"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MIGRATIONS_DIR="$PROJECT_ROOT/migrations"

echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}PostgreSQL Setup for Phase 4 - Legal Data Collection${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""

# ============================================================================
# 1. Check if PostgreSQL is already installed
# ============================================================================
echo -e "${YELLOW}[1/8] Checking PostgreSQL installation...${NC}"

if command -v psql &> /dev/null; then
    INSTALLED_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)
    echo -e "${GREEN}✓ PostgreSQL $INSTALLED_VERSION is already installed${NC}"

    if [ "$INSTALLED_VERSION" -lt "$POSTGRES_VERSION" ]; then
        echo -e "${YELLOW}⚠ Warning: Installed version ($INSTALLED_VERSION) is older than recommended ($POSTGRES_VERSION)${NC}"
        read -p "Do you want to upgrade? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Continuing with existing version..."
            POSTGRES_VERSION=$INSTALLED_VERSION
        fi
    fi
else
    echo -e "${YELLOW}PostgreSQL not found. Installing PostgreSQL $POSTGRES_VERSION...${NC}"

    # Update package list
    sudo apt-get update

    # Install PostgreSQL
    sudo apt-get install -y postgresql-$POSTGRES_VERSION postgresql-contrib-$POSTGRES_VERSION

    echo -e "${GREEN}✓ PostgreSQL $POSTGRES_VERSION installed successfully${NC}"
fi

# ============================================================================
# 2. Start PostgreSQL service
# ============================================================================
echo -e "\n${YELLOW}[2/8] Starting PostgreSQL service...${NC}"

sudo service postgresql start || sudo systemctl start postgresql

# Check if running
if sudo service postgresql status | grep -q "online" || sudo systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL service is running${NC}"
else
    echo -e "${RED}✗ Failed to start PostgreSQL service${NC}"
    exit 1
fi

# ============================================================================
# 3. Create database user
# ============================================================================
echo -e "\n${YELLOW}[3/8] Creating database user...${NC}"

# Check if user already exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo -e "${YELLOW}User '$DB_USER' already exists${NC}"
    read -p "Do you want to reset the password? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        echo -e "${GREEN}✓ Password updated for user '$DB_USER'${NC}"
    fi
else
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo -e "${GREEN}✓ Created user '$DB_USER'${NC}"
fi

# Grant superuser privileges (needed for creating extensions)
sudo -u postgres psql -c "ALTER USER $DB_USER WITH SUPERUSER;"

# ============================================================================
# 4. Create database
# ============================================================================
echo -e "\n${YELLOW}[4/8] Creating database...${NC}"

# Check if database already exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}Database '$DB_NAME' already exists${NC}"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo -u postgres psql -c "DROP DATABASE $DB_NAME;"
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        echo -e "${GREEN}✓ Database '$DB_NAME' recreated${NC}"
    fi
else
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    echo -e "${GREEN}✓ Created database '$DB_NAME'${NC}"
fi

# Grant all privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# ============================================================================
# 5. Configure PostgreSQL for performance
# ============================================================================
echo -e "\n${YELLOW}[5/8] Configuring PostgreSQL for performance...${NC}"

# Get PostgreSQL config file location
PG_CONF=$(sudo -u postgres psql -tAc "SHOW config_file")

echo "PostgreSQL config file: $PG_CONF"

# Backup existing config
sudo cp "$PG_CONF" "${PG_CONF}.backup.$(date +%Y%m%d_%H%M%S)"

# Performance tuning settings
echo -e "\n${YELLOW}Applying performance optimizations...${NC}"

# These settings are optimized for a machine with 16GB RAM and high-volume writes
sudo sed -i "s/^#*max_connections = .*/max_connections = 200/" "$PG_CONF"
sudo sed -i "s/^#*shared_buffers = .*/shared_buffers = 4GB/" "$PG_CONF"
sudo sed -i "s/^#*effective_cache_size = .*/effective_cache_size = 12GB/" "$PG_CONF"
sudo sed -i "s/^#*maintenance_work_mem = .*/maintenance_work_mem = 1GB/" "$PG_CONF"
sudo sed -i "s/^#*checkpoint_completion_target = .*/checkpoint_completion_target = 0.9/" "$PG_CONF"
sudo sed -i "s/^#*wal_buffers = .*/wal_buffers = 16MB/" "$PG_CONF"
sudo sed -i "s/^#*default_statistics_target = .*/default_statistics_target = 100/" "$PG_CONF"
sudo sed -i "s/^#*random_page_cost = .*/random_page_cost = 1.1/" "$PG_CONF"  # SSD optimization
sudo sed -i "s/^#*effective_io_concurrency = .*/effective_io_concurrency = 200/" "$PG_CONF"  # SSD
sudo sed -i "s/^#*work_mem = .*/work_mem = 20MB/" "$PG_CONF"
sudo sed -i "s/^#*min_wal_size = .*/min_wal_size = 1GB/" "$PG_CONF"
sudo sed -i "s/^#*max_wal_size = .*/max_wal_size = 4GB/" "$PG_CONF"

echo -e "${GREEN}✓ Performance settings applied${NC}"

# Restart PostgreSQL to apply changes
echo -e "\n${YELLOW}Restarting PostgreSQL to apply configuration...${NC}"
sudo service postgresql restart || sudo systemctl restart postgresql
sleep 2

echo -e "${GREEN}✓ PostgreSQL restarted${NC}"

# ============================================================================
# 6. Create extensions
# ============================================================================
echo -e "\n${YELLOW}[6/8] Creating PostgreSQL extensions...${NC}"

# Full-text search extension
psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" 2>/dev/null || \
    sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
echo -e "${GREEN}✓ Created pg_trgm extension (trigram matching for full-text search)${NC}"

# UUID extension
psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null || \
    sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
echo -e "${GREEN}✓ Created uuid-ossp extension${NC}"

# ============================================================================
# 7. Run migrations
# ============================================================================
echo -e "\n${YELLOW}[7/8] Running database migrations...${NC}"

if [ -d "$MIGRATIONS_DIR" ]; then
    echo "Migrations directory: $MIGRATIONS_DIR"

    # Run all .sql files in order
    for migration in "$MIGRATIONS_DIR"/*.sql; do
        if [ -f "$migration" ]; then
            echo -e "Running: $(basename $migration)"
            PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -f "$migration"
            echo -e "${GREEN}✓ $(basename $migration) completed${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠ Migrations directory not found: $MIGRATIONS_DIR${NC}"
    echo "Skipping migrations. You can run them manually later."
fi

# ============================================================================
# 8. Verify setup
# ============================================================================
echo -e "\n${YELLOW}[8/8] Verifying setup...${NC}"

# Test connection
if PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -c "\conninfo" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    echo "Trying with sudo..."
    sudo -u postgres psql -d $DB_NAME -c "\conninfo"
fi

# Check tables
TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
echo -e "${GREEN}✓ Found $TABLE_COUNT tables in database${NC}"

# Database size
DB_SIZE=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -tAc "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
echo -e "${GREEN}✓ Database size: $DB_SIZE${NC}"

# Connection info
echo -e "\n${GREEN}============================================================================${NC}"
echo -e "${GREEN}PostgreSQL Setup Complete!${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "Database Details:"
echo -e "  Host:     localhost"
echo -e "  Port:     $DB_PORT"
echo -e "  Database: $DB_NAME"
echo -e "  User:     $DB_USER"
echo -e "  Password: $DB_PASSWORD"
echo ""
echo -e "Connection String:"
echo -e "  ${YELLOW}postgresql://$DB_USER:$DB_PASSWORD@localhost:$DB_PORT/$DB_NAME${NC}"
echo ""
echo -e "Test Connection:"
echo -e "  ${YELLOW}PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME${NC}"
echo ""
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Config already updated in config/config_production.yaml ✓"
echo -e "  2. Run: ${YELLOW}python scripts/migrate_sqlite_to_pg.py${NC} to migrate existing data"
echo -e "  3. Test the scraper with PostgreSQL backend"
echo ""
echo -e "${GREEN}Done! ✓${NC}"
