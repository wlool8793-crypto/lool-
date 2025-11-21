#!/bin/bash
# Setup PostgreSQL for IndianKanoon Scraper
# Run this script to initialize the PostgreSQL database

set -e  # Exit on error

echo "==================================================================="
echo "IndianKanoon Scraper - PostgreSQL Setup"
echo "==================================================================="

# Database configuration
DB_NAME="indiankanoon"
DB_USER="codespace"  # Using current user for peer authentication
DB_HOST="localhost"
DB_PORT="5432"

echo "Step 1: Creating database '$DB_NAME'..."
createdb -h $DB_HOST -p $DB_PORT $DB_NAME 2>/dev/null || echo "Database '$DB_NAME' may already exist"

echo "Step 2: Verifying database connection..."
psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "SELECT version();" > /dev/null && echo "✓ Connection successful" || {
    echo "✗ Failed to connect to database"
    exit 1
}

echo "Step 3: Creating database schema (via SQLAlchemy)..."
python3 << EOF
import sys
sys.path.insert(0, '/workspaces/lool-/data-collection')
from src.database import Base
from sqlalchemy import create_engine

# Create engine and tables
engine = create_engine('postgresql://codespace@localhost:5432/$DB_NAME')
Base.metadata.create_all(engine)
print("✓ Database schema created successfully")
EOF

echo ""
echo "==================================================================="
echo "✓ PostgreSQL setup complete!"
echo "==================================================================="
echo ""
echo "Connection details:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo ""
echo "Connection string:"
echo "  DATABASE_URL=postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "Update your .env file with this connection string."
echo "==================================================================="
