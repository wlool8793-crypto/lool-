# LangGraph Deep Web Agent - Dockerfile
# Multi-stage build for production optimization

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    nginx \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache /app/uploads /app/backups

# Set permissions
RUN chown -R appuser:appuser /app
RUN chmod +x scripts/init_db.py scripts/migrate_db.py 2>/dev/null || true

# Copy configuration files
COPY config/nginx.conf /etc/nginx/nginx.conf 2>/dev/null || true
COPY config/supervisor.conf /etc/supervisor/conf.d/supervisor.conf 2>/dev/null || true

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh 2>/dev/null || true
RUN chmod +x /entrypoint.sh 2>/dev/null || true

# Expose ports
EXPOSE 8000 80 443

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Entry point
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisor.conf"]