#!/bin/bash

# Development setup script for Deep Agent
set -e

echo "🚀 Deep Agent Development Setup"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/deep_agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=deep_agent

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=your-pinecone-environment

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000

# External API Keys
GOOGLE_API_KEY=
GITHUB_TOKEN=

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Security
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
EOF
    echo "✅ .env file created. Please update it with your API keys."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs alembic/versions

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test database connection
echo "🔍 Testing database connection..."
python scripts/test_db_connection.py

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"

    # Initialize database
    echo "📋 Initializing database..."
    python scripts/init_db.py

    echo ""
    echo "🎉 Development setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update your .env file with actual API keys"
    echo "2. Start the application: uvicorn app.main:app --reload"
    echo "3. Access API docs: http://localhost:8000/docs"
    echo "4. View application: http://localhost:8000"
    echo ""
    echo "Useful commands:"
    echo "- Start services: docker-compose up -d"
    echo "- Stop services: docker-compose down"
    echo "- View logs: docker-compose logs -f"
    echo "- Test database: python scripts/test_db_connection.py"
    echo "- Run migrations: python scripts/migrate_db.py migrate"
else
    echo "❌ Database connection failed. Please check the logs:"
    echo "docker-compose logs postgres"
    echo "docker-compose logs redis"
    exit 1
fi