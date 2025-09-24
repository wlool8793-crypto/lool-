#!/bin/bash
set -e

# LangGraph Deep Web Agent - Docker Entrypoint Script

echo "=== LangGraph Deep Web Agent Container Starting ==="

# Wait for dependencies to be ready
echo "Waiting for dependencies..."

# Wait for PostgreSQL
if [ "$DATABASE_URL" != "" ]; then
    echo "Waiting for PostgreSQL to be ready..."
    while ! nc -z postgres 5432; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "PostgreSQL is up - continuing"
fi

# Wait for Redis
if [ "$REDIS_URL" != "" ]; then
    echo "Waiting for Redis to be ready..."
    while ! nc -z redis 6379; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done
    echo "Redis is up - continuing"
fi

# Wait for RabbitMQ
if [ "$CELERY_BROKER_URL" != "" ]; then
    echo "Waiting for RabbitMQ to be ready..."
    while ! nc -z rabbitmq 5672; do
        echo "RabbitMQ is unavailable - sleeping"
        sleep 2
    done
    echo "RabbitMQ is up - continuing"
fi

# Run database migrations
echo "Running database migrations..."
if [ -f "scripts/migrate_db.py" ]; then
    python scripts/migrate_db.py
else
    echo "Migration script not found, skipping..."
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /app/logs /app/data /app/cache /app/uploads /app/backups

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 /app/logs /app/data /app/cache /app/uploads /app/backups

# Generate Django secret key if not provided
if [ "$SECRET_KEY" = "" ]; then
    echo "Generating secret key..."
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
fi

# Initialize security configuration
echo "Initializing security configuration..."
if [ -f "app/security/security_config.py" ]; then
    python -c "
import sys
sys.path.append('/app')
from app.security.security_config import SecurityConfigManager
from app.security.encryption import EncryptionManager
from app.security.audit_logging import AuditLogger
print('Security components initialized successfully')
"
fi

# Health check function
health_check() {
    local max_attempts=30
    local attempt=1

    echo "Performing health check..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "Health check passed!"
            return 0
        fi

        echo "Health check attempt $attempt/$max_attempts failed..."
        sleep 2
        ((attempt++))
    done

    echo "Health check failed after $max_attempts attempts"
    return 1
}

# Start the application based on the command
echo "Starting application..."
case "$1" in
    "web")
        echo "Starting FastAPI web server..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
        ;;
    "worker")
        echo "Starting Celery worker..."
        exec celery -A app.celery worker --loglevel=info
        ;;
    "beat")
        echo "Starting Celery beat scheduler..."
        exec celery -A app.celery beat --loglevel=info
        ;;
    "dev")
        echo "Starting development server..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
        ;;
    "test")
        echo "Running tests..."
        exec python -m pytest tests/ -v
        ;;
    "migrate")
        echo "Running database migrations..."
        exec python scripts/migrate_db.py
        ;;
    "shell")
        echo "Starting shell..."
        exec /bin/bash
        ;;
    *)
        # Default: start with supervisord
        echo "Starting with supervisord..."

        # Create supervisor config if it doesn't exist
        if [ ! -f "/etc/supervisor/conf.d/supervisor.conf" ]; then
            echo "Creating supervisor configuration..."
            mkdir -p /etc/supervisor/conf.d
            cat > /etc/supervisor/conf.d/supervisor.conf << EOF
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:web]
command=uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/app
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/web.log
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1",PYTHONDONTWRITEBYTECODE="1"

[program:worker]
command=celery -A app.celery worker --loglevel=info
directory=/app
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/worker.log
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1",PYTHONDONTWRITEBYTECODE="1"

[program:beat]
command=celery -A app.celery beat --loglevel=info
directory=/app
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/beat.log
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1",PYTHONDONTWRITEBYTECODE="1"
EOF
        fi

        # Start supervisord
        exec supervisord -c /etc/supervisor/conf.d/supervisor.conf
        ;;
esac

# Run health check if web server is starting
if [[ "$1" == "web" || "$1" == "" ]]; then
    sleep 5  # Give the server time to start
    if ! health_check; then
        echo "Health check failed!"
        exit 1
    fi
fi

echo "=== LangGraph Deep Web Agent Container Started Successfully ==="