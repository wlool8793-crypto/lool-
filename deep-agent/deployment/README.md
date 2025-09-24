# Deployment Guide

This guide covers all aspects of deploying the LangGraph Deep Web Agent system to production environments.

## Table of Contents

- [Deployment Strategies](#deployment-strategies)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Database Migration](#database-migration)
- [Security Configuration](#security-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Deployment Strategies

### 1. Blue-Green Deployment

Blue-green deployment minimizes downtime by maintaining two identical production environments:

```bash
# Deploy to green environment
./scripts/deploy.sh deploy --environment=green

# Switch traffic to green
./scripts/deploy.sh switch-traffic --to=green

# Keep blue environment for rollback
./scripts/deploy.sh keep-blue --duration=24h
```

### 2. Canary Deployment

Gradual rollout to a subset of users:

```bash
# Deploy canary to 10% of traffic
./scripts/deploy.sh deploy --strategy=canary --traffic=10

# Monitor canary performance
./scripts/deploy.sh monitor --environment=canary

# Promote to full production
./scripts/deploy.sh promote --from=canary
```

### 3. Rolling Deployment

Gradual replacement of instances:

```bash
# Rolling deployment with 5% increments
./scripts/deploy.sh deploy --strategy=rolling --increment=5

# Monitor during rollout
./scripts/deploy.sh monitor --rolling=true
```

## Prerequisites

### System Requirements

- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM recommended
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection
- **Docker**: 20.10+
- **Kubernetes**: 1.25+ (for K8s deployment)

### Software Requirements

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose
- kubectl and helm (for Kubernetes)

### External Dependencies

- Domain name with SSL certificate
- Container registry (Docker Hub, GHCR, ECR)
- Database hosting (managed PostgreSQL recommended)
- Redis hosting (managed Redis recommended)
- Monitoring and logging services

## Environment Setup

### 1. Environment Variables

Create `.env.production`:

```bash
# Application Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secure-secret-key-here
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/deep_agent
DATABASE_SSL_MODE=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
REDIS_SSL=true

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=20

# External API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# Cloud Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENDPOINT=http://localhost:9090
GRAFANA_URL=http://localhost:3000

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@your-domain.com

# Webhook Configuration
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_TIMEOUT=30
```

### 2. SSL/TLS Certificates

Generate SSL certificates using Let's Encrypt:

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Docker Deployment

### 1. Production Docker Compose

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/your-username/deep-agent:latest
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: ghcr.io/your-username/deep-agent-frontend:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=https://api.your-domain.com
      - REACT_APP_WS_URL=wss://api.your-domain.com/ws
    depends_on:
      - backend

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=deep_agent
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### 2. Deployment Script

Run production deployment:

```bash
# Set environment variables
export $(cat .env.production | xargs)

# Pull latest images
docker-compose -f docker-compose.production.yml pull

# Deploy with zero downtime
docker-compose -f docker-compose.production.yml up -d --remove-orphans

# Run database migrations
docker-compose -f docker-compose.production.yml exec backend python -m alembic upgrade head

# Verify deployment
curl -f https://your-domain.com/health
```

## Kubernetes Deployment

### 1. Namespace and Secrets

```bash
# Create namespace
kubectl create namespace deep-agent

# Create secrets
kubectl create secret generic deep-agent-secrets \
  --from-env-file=.env.production \
  --namespace=deep-agent

# Create TLS secret
kubectl create secret tls deep-agent-tls \
  --cert=/path/to/fullchain.pem \
  --key=/path/to/privkey.pem \
  --namespace=deep-agent
```

### 2. Deploy Application

```bash
# Deploy database
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Deploy backend
kubectl apply -f k8s/backend.yaml

# Deploy frontend
kubectl apply -f k8s/frontend.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Monitor rollout
kubectl rollout status deployment/deep-agent-backend -n deep-agent
```

### 3. Helm Deployment

```bash
# Add Helm repository
helm repo add deep-agent https://charts.deep-agent.com

# Install chart
helm install deep-agent deep-agent/deep-agent \
  --namespace deep-agent \
  --values values.yaml \
  --wait

# Upgrade deployment
helm upgrade deep-agent deep-agent/deep-agent \
  --namespace deep-agent \
  --values values.yaml \
  --wait
```

## Cloud Deployment

### AWS Deployment

#### 1. ECS Deployment

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name deep-agent-cluster

# Create task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster deep-agent-cluster \
  --service-name deep-agent-service \
  --task-definition deep-agent-task:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:region:account-id:targetgroup/my-target-group/ID,containerName=deep-agent,containerPort=8000
```

#### 2. RDS and ElastiCache

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier deep-agent-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username deepagent \
  --master-user-password secure-password \
  --allocated-storage 20

# Create ElastiCache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id deep-agent-cache \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1 \
  --security-group-ids sg-12345678
```

### Google Cloud Deployment

#### 1. Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT-ID/deep-agent-backend
gcloud run deploy deep-agent-backend \
  --image gcr.io/PROJECT-ID/deep-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/deep-agent-frontend
gcloud run deploy deep-agent-frontend \
  --image gcr.io/PROJECT-ID/deep-agent-frontend \
  --platform managed \
  --region us-central1
```

### Azure Deployment

#### 1. Azure Container Instances

```bash
# Create resource group
az group create --name deep-agent-rg --location eastus

# Create container instance
az container create \
  --resource-group deep-agent-rg \
  --name deep-agent-backend \
  --image ghcr.io/your-username/deep-agent:latest \
  --dns-name-label deep-agent-backend \
  --ports 8000 \
  --environment-variables \
    'DATABASE_URL'='${DATABASE_URL}' \
    'REDIS_URL'='${REDIS_URL}'
```

## Database Migration

### 1. Migration Strategy

```bash
# Create backup before migration
./scripts/deploy.sh backup --database

# Run migrations
./scripts/deploy.sh migrate --env=production

# Verify migration
./scripts/deploy.sh verify-migration

# Rollback if needed
./scripts/deploy.sh rollback-migration --version=previous
```

### 2. Data Seeding

```bash
# Seed initial data
python scripts/seed_data.py --env=production

# Seed configuration
python scripts/seed_config.py --env=production

# Seed default users
python scripts/seed_users.py --env=production
```

## Security Configuration

### 1. Network Security

```bash
# Configure security groups
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

# Configure WAF rules
aws waf create-web-acl --name deep-agent-waf --metric-name deep-agent-waf
```

### 2. Application Security

```python
# Configure security headers
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'",
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block'
}
```

## Monitoring and Logging

### 1. Prometheus Monitoring

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'deep-agent'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### 2. Grafana Dashboard

Create comprehensive dashboards for:
- Application metrics
- Database performance
- Redis performance
- System resources
- Error rates
- Response times

### 3. Logging Configuration

```yaml
# logging.yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: standard
    filename: /var/log/deep-agent/app.log
    maxBytes: 10485760
    backupCount: 5

loggers:
  '':
    level: INFO
    handlers: [console, file]
    propagate: false
```

## Backup and Recovery

### 1. Database Backup

```bash
# Daily backup
0 2 * * * /usr/local/bin/backup-database.sh

# Weekly full backup
0 3 * * 0 /usr/local/bin/backup-full.sh

# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U deepagent deep_agent > /backups/db_$DATE.sql
gzip /backups/db_$DATE.sql
```

### 2. Recovery Procedure

```bash
# Stop application
docker-compose -f docker-compose.production.yml stop

# Restore database
gunzip < /backups/db_latest.sql.gz | psql -h localhost -U deepagent deep_agent

# Restart application
docker-compose -f docker-compose.production.yml start

# Verify recovery
curl -f https://your-domain.com/health
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check database connectivity
docker-compose -f docker-compose.production.yml exec backend python -c "
from app.core.database import engine
print(engine.connect())
"

# Check database logs
docker-compose -f docker-compose.production.yml logs postgres
```

#### 2. Redis Connection Issues

```bash
# Check Redis connectivity
docker-compose -f docker-compose.production.yml exec redis redis-cli ping

# Check Redis logs
docker-compose -f docker-compose.production.yml logs redis
```

#### 3. Application Startup Issues

```bash
# Check application logs
docker-compose -f docker-compose.production.yml logs backend

# Check health endpoint
curl -f http://localhost:8000/health

# Check database migrations
docker-compose -f docker-compose.production.yml exec backend python -m alembic current
```

### Performance Issues

#### 1. High Memory Usage

```bash
# Check memory usage
docker stats

# Monitor memory leaks
docker-compose -f docker-compose.production.yml exec backend python -m memory_profiler app.main:app
```

#### 2. High CPU Usage

```bash
# Check CPU usage
top

# Profile CPU usage
docker-compose -f docker-compose.production.yml exec backend python -m cProfile -o profile.prof app.main:app
```

### Health Check Endpoints

- `/health` - Overall system health
- `/api/v1/health` - API health
- `/api/v1/health/database` - Database health
- `/api/v1/health/redis` - Redis health
- `/metrics` - Prometheus metrics

### Emergency Procedures

#### 1. Emergency Rollback

```bash
# Rollback to previous version
./scripts/deploy.sh rollback --version=previous

# Emergency maintenance mode
./scripts/deploy.sh maintenance --enable

# Emergency database recovery
./scripts/deploy.sh restore-database --backup=latest
```

#### 2. Disaster Recovery

```bash
# Deploy to backup region
./scripts/deploy.sh deploy --region=backup --emergency=true

# Switch DNS to backup
./scripts/deploy.sh failover --to=backup

# Restore from backup
./scripts/deploy.sh restore --from-backup --full=true
```

## Support

For deployment issues and support:

- Check the [troubleshooting guide](troubleshooting.md)
- Review [monitoring dashboards](monitoring.md)
- Contact the operations team
- Create an issue in the project repository