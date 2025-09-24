#!/bin/bash

# LangGraph Deep Web Agent - Production Deployment Script

set -e

echo "=== LangGraph Deep Web Agent - Production Deployment ==="

# Configuration
PROJECT_NAME="deep-agent"
REGISTRY="${REGISTRY:-your-registry}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DEPLOY_ENV="${DEPLOY_ENV:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check kubectl if Kubernetes deployment
    if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl is not installed"
            exit 1
        fi
    fi

    # Check environment files
    if [ ! -f ".env.production" ]; then
        log_error "Production environment file not found"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."

    # Build main application image
    docker build -t "${REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}" .

    # Build frontend image if exists
    if [ -d "frontend" ]; then
        log_info "Building frontend image..."
        cd frontend
        docker build -t "${REGISTRY}/${PROJECT_NAME}-frontend:${IMAGE_TAG}" .
        cd ..
    fi

    # Push images to registry
    if [ "$REGISTRY" != "your-registry" ]; then
        log_info "Pushing images to registry..."
        docker push "${REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}"
        docker push "${REGISTRY}/${PROJECT_NAME}-frontend:${IMAGE_TAG}"
    fi

    log_info "Images built successfully"
}

# Deploy with Docker Compose
deploy_compose() {
    log_info "Deploying with Docker Compose..."

    # Create production environment file
    cp .env.production .env

    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose down

    # Pull latest images
    log_info "Pulling latest images..."
    docker-compose pull

    # Start services
    log_info "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30

    # Check health status
    check_health

    log_info "Docker Compose deployment completed"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."

    # Create namespace if not exists
    kubectl create namespace ${PROJECT_NAME} --dry-run=client -o yaml | kubectl apply -f -

    # Create secrets
    log_info "Creating Kubernetes secrets..."
    kubectl create secret generic ${PROJECT_NAME}-secrets \
        --from-env-file=.env.production \
        --namespace=${PROJECT_NAME} \
        --dry-run=client -o yaml | kubectl apply -f -

    # Deploy manifests
    log_info "Applying Kubernetes manifests..."
    if [ -d "k8s" ]; then
        kubectl apply -f k8s/ -n ${PROJECT_NAME}
    else
        log_warn "Kubernetes manifests directory not found"
    fi

    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/${PROJECT_NAME} -n ${PROJECT_NAME}

    # Check health status
    check_health_k8s

    log_info "Kubernetes deployment completed"
}

# Health check for Docker Compose
check_health() {
    log_info "Performing health check..."

    # Check if backend is responding
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi

    # Check if frontend is responding
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "Frontend health check passed"
    else
        log_warn "Frontend health check failed (may be starting up)"
    fi

    # Check database connectivity
    if docker-compose exec postgres pg_isready -U deepagent_user -d deep_agent > /dev/null 2>&1; then
        log_info "Database health check passed"
    else
        log_error "Database health check failed"
        exit 1
    fi

    # Check Redis connectivity
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        log_info "Redis health check passed"
    else
        log_error "Redis health check failed"
        exit 1
    fi
}

# Health check for Kubernetes
check_health_k8s() {
    log_info "Performing Kubernetes health check..."

    # Check pod status
    kubectl get pods -n ${PROJECT_NAME}

    # Check services
    kubectl get services -n ${PROJECT_NAME}

    # Get ingress information
    if kubectl get ingress -n ${PROJECT_NAME} &> /dev/null; then
        kubectl get ingress -n ${PROJECT_NAME}
    fi

    log_info "Kubernetes health check completed"
}

# Backup and restore
backup_data() {
    log_info "Creating backup..."

    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR

    # Backup database
    log_info "Backing up database..."
    docker-compose exec postgres pg_dump -U deepagent_user deep_agent > ${BACKUP_DIR}/database.sql

    # Backup Redis data
    log_info "Backing up Redis data..."
    docker-compose exec redis redis-cli --rdb $BACKUP_DIR/redis.rdb

    # Backup configuration files
    log_info "Backing up configuration..."
    cp .env.production ${BACKUP_DIR}/

    log_info "Backup created at ${BACKUP_DIR}"
}

# Rollback deployment
rollback() {
    log_warn "Rolling back deployment..."

    if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
        # Rollback Kubernetes deployment
        kubectl rollout undo deployment/${PROJECT_NAME} -n ${PROJECT_NAME}
        kubectl wait --for=condition=available --timeout=300s deployment/${PROJECT_NAME} -n ${PROJECT_NAME}
    else
        # Rollback Docker Compose
        docker-compose down
        docker-compose up -d
    fi

    log_info "Rollback completed"
}

# Cleanup
cleanup() {
    log_info "Cleaning up old resources..."

    # Remove unused Docker images
    docker image prune -f

    # Remove unused volumes
    docker volume prune -f

    # Remove unused networks
    docker network prune -f

    log_info "Cleanup completed"
}

# Main deployment function
main() {
    # Parse command line arguments
    case "${1:-deploy}" in
        "prerequisites")
            check_prerequisites
            ;;
        "build")
            build_images
            ;;
        "deploy")
            check_prerequisites
            build_images
            if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
                deploy_kubernetes
            else
                deploy_compose
            fi
            ;;
        "health")
            if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
                check_health_k8s
            else
                check_health
            fi
            ;;
        "backup")
            backup_data
            ;;
        "rollback")
            rollback
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
                kubectl logs -f deployment/${PROJECT_NAME} -n ${PROJECT_NAME}
            else
                docker-compose logs -f
            fi
            ;;
        "status")
            if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
                kubectl get all -n ${PROJECT_NAME}
            else
                docker-compose ps
            fi
            ;;
        "stop")
            if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
                kubectl scale deployment/${PROJECT_NAME} --replicas=0 -n ${PROJECT_NAME}
            else
                docker-compose down
            fi
            ;;
        "start")
            if [ "$DEPLOY_TYPE" = "kubernetes" ]; then
                kubectl scale deployment/${PROJECT_NAME} --replicas=3 -n ${PROJECT_NAME}
            else
                docker-compose up -d
            fi
            ;;
        *)
            echo "Usage: $0 {prerequisites|build|deploy|health|backup|rollback|cleanup|logs|status|stop|start}"
            echo ""
            echo "Environment Variables:"
            echo "  REGISTRY          Docker registry (default: your-registry)"
            echo "  IMAGE_TAG         Image tag (default: latest)"
            echo "  DEPLOY_ENV        Deployment environment (default: production)"
            echo "  DEPLOY_TYPE       Deployment type: compose|kubernetes (default: compose)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

echo "=== Deployment completed successfully ==="