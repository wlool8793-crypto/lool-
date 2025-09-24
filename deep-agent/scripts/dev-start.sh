#!/bin/bash

# LangGraph Deep Web Agent - Development Startup Script

set -e

echo "=== LangGraph Deep Web Agent - Development Environment ==="

# Configuration
PROJECT_NAME="deep-agent"
COMPOSE_FILE="docker-compose.yml"
COMPOSE_OVERRIDE="docker-compose.override.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is running
check_docker() {
    log_step "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_info "Docker is running"
}

# Create necessary directories
create_directories() {
    log_step "Creating necessary directories..."
    mkdir -p logs data cache uploads backups
    log_info "Directories created"
}

# Create environment files
create_env_files() {
    log_step "Setting up environment files..."

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# LangGraph Deep Web Agent - Development Environment

# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/deep_agent

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=1

# API Keys (add your actual keys)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# External Services
RABBITMQ_PASSWORD=rabbitmq_password
REDIS_PASSWORD=redis_password
POSTGRES_PASSWORD=password

# Development Settings
PYTHONPATH=/app
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
EOF
        log_info "Created .env file"
    else
        log_info ".env file already exists"
    fi
}

# Install Python dependencies
install_dependencies() {
    log_step "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        if command -v pip &> /dev/null; then
            pip install -r requirements.txt
            log_info "Python dependencies installed"
        else
            log_warn "pip not found, skipping Python dependencies installation"
        fi
    else
        log_warn "requirements.txt not found"
    fi
}

# Install frontend dependencies
install_frontend_deps() {
    log_step "Installing frontend dependencies..."
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        if command -v npm &> /dev/null; then
            cd frontend
            npm install
            cd ..
            log_info "Frontend dependencies installed"
        else
            log_warn "npm not found, skipping frontend dependencies installation"
        fi
    else
        log_warn "Frontend directory or package.json not found"
    fi
}

# Database setup
setup_database() {
    log_step "Setting up database..."

    # Create database initialization script if it doesn't exist
    if [ ! -f "scripts/init.sql" ]; then
        mkdir -p scripts
        cat > scripts/init.sql << EOF
-- LangGraph Deep Web Agent - Database Initialization

CREATE DATABASE IF NOT EXISTS deep_agent;
CREATE USER IF NOT EXISTS deepagent_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE deep_agent TO deepagent_user;
EOF
        log_info "Created database initialization script"
    fi

    # Run database migrations
    if [ -f "scripts/migrate_db.py" ]; then
        if command -v python &> /dev/null; then
            python scripts/migrate_db.py
            log_info "Database migrations completed"
        else
            log_warn "Python not found, skipping database migrations"
        fi
    fi
}

# Start services with Docker Compose
start_services() {
    log_step "Starting services with Docker Compose..."

    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE down

    # Build and start services
    log_info "Building and starting services..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE up -d --build

    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 20

    # Check service status
    log_step "Checking service status..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE ps

    # Show logs
    log_info "Recent logs:"
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE logs --tail=20
}

# Run development server locally
run_local_server() {
    log_step "Starting local development server..."

    if command -v python &> /dev/null; then
        log_info "Starting FastAPI development server..."
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug &

        if [ -d "frontend" ]; then
            log_info "Starting React development server..."
            cd frontend
            npm start &
            cd ..
        fi

        log_info "Development servers started"
        log_info "Backend: http://localhost:8000"
        log_info "Frontend: http://localhost:3000"
        log_info "API Docs: http://localhost:8000/docs"

        # Wait for user input
        log_info "Press Ctrl+C to stop the servers"
        wait
    else
        log_error "Python not found. Cannot start local development server."
        exit 1
    fi
}

# Run tests
run_tests() {
    log_step "Running tests..."

    if command -v python &> /dev/null; then
        if [ -d "tests" ]; then
            # Run backend tests
            python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

            # Run frontend tests if exists
            if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
                cd frontend
                if grep -q "test" package.json; then
                    npm test
                else
                    log_info "No frontend tests configured"
                fi
                cd ..
            fi
        else
            log_warn "No tests directory found"
        fi
    else
        log_warn "Python not found, skipping tests"
    fi
}

# Show status
show_status() {
    log_step "Current status:"

    # Docker Compose status
    if command -v docker-compose &> /dev/null; then
        echo -e "${BLUE}Docker Services:${NC}"
        docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE ps
    fi

    # Show URLs
    echo -e "${BLUE}Service URLs:${NC}"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Frontend: http://localhost:3000"
    echo "  Redis Commander: http://localhost:8081"
    echo "  RabbitMQ Management: http://localhost:15672"

    # Show useful commands
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs: docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE logs -f [service]"
    echo "  Stop services: docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE down"
    echo "  Restart services: docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE restart"
    echo "  Run tests: ./scripts/dev-start.sh test"
}

# Stop services
stop_services() {
    log_step "Stopping services..."
    docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE down
    log_info "Services stopped"
}

# Main function
main() {
    case "${1:-start}" in
        "check")
            check_docker
            ;;
        "setup")
            check_docker
            create_directories
            create_env_files
            install_dependencies
            install_frontend_deps
            setup_database
            ;;
        "deps")
            install_dependencies
            install_frontend_deps
            ;;
        "db")
            setup_database
            ;;
        "start")
            check_docker
            start_services
            show_status
            ;;
        "local")
            check_docker
            run_local_server
            ;;
        "test")
            run_tests
            ;;
        "logs")
            if [ -n "$2" ]; then
                docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE logs -f "$2"
            else
                docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE logs -f
            fi
            ;;
        "status")
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services
            ;;
        "reset")
            stop_services
            docker-compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE down -v
            docker system prune -f
            log_info "Environment reset"
            ;;
        *)
            echo "Usage: $0 {check|setup|deps|db|start|local|test|logs [service]|status|stop|restart|reset}"
            echo ""
            echo "Commands:"
            echo "  check      - Check Docker status"
            echo "  setup      - Full environment setup"
            echo "  deps       - Install dependencies only"
            echo "  db         - Database setup only"
            echo "  start      - Start services with Docker Compose"
            echo "  local      - Run development servers locally"
            echo "  test       - Run tests"
            echo "  logs       - Show logs (optional: specify service)"
            echo "  status     - Show current status"
            echo "  stop       - Stop all services"
            echo "  restart    - Restart all services"
            echo "  reset      - Reset environment (remove all containers and volumes)"
            echo ""
            echo "Examples:"
            echo "  $0 setup          # Full setup"
            echo "  $0 start          # Start Docker services"
            echo "  $0 local          # Run local development servers"
            echo "  $0 logs backend   # Show backend logs"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

echo "=== Development environment ready! ==="