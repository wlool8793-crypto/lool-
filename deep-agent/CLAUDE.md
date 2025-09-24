# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Development Status (Updated: 2025-09-22)

### ✅ Completed Tasks
- **Phase 1-40**: Complete system implementation including backend, frontend, database, security, deployment
- **Environment Setup**: All core dependencies installed and configured
- **Backend Server**: FastAPI server running on port 8000 (with minor warnings)
- **Frontend Dependencies**: All npm packages installed successfully
- **Database Models**: PostgreSQL models configured with proper field naming
- **Agent System**: LangGraph orchestration with specialized nodes
- **Security Framework**: JWT authentication, RBAC, and API security
- **CI/CD Pipeline**: GitHub Actions workflows configured

### 🔄 Current Status
- **Backend**: ✅ Running on `http://localhost:8000` (minor dependency warnings)
- **Frontend**: 📋 Dependencies installed, ready to start on port 3000
- **Database**: ⚠️ PostgreSQL connection needed (service not started)
- **Redis**: ⚠️ Redis connection needed (service not started)
- **Tests**: 📋 Test framework configured, ready to run

### 📋 Next Steps for Tomorrow
1. **Start PostgreSQL**: `sudo service postgresql start` or use Docker
2. **Start Redis**: `redis-server` or use Docker
3. **Frontend Server**: `npm start` to start React development server
4. **Test Integration**: Verify frontend-backend communication
5. **Database Migrations**: Run `python -m alembic upgrade head`
6. **End-to-End Testing**: Test complete agent workflows

### 🔧 Known Issues to Address
- **PostgreSQL**: Service needs to be started (`sudo service postgresql start`)
- **Redis**: Service needs to be started (`redis-server`)
- **Email validator**: Package installed but may need additional configuration
- **ToolExecutor**: Deprecated import commented out in `app/agents/graph_builder.py:6`

### 📁 Working Directory Context
- **Backend**: Running on port 8000 with automatic reload
- **Frontend**: Dependencies installed in `/workspaces/lool-/deep-agent/node_modules/`
- **Configuration**: `.env` file with dummy API keys for development
- **Database**: Models configured with proper field naming (`metadata` → `meta_data`)
- **Dependencies**: All Python and npm packages installed

### 💡 Quick Start Commands for Tomorrow
```bash
# Start database services
sudo service postgresql start
redis-server

# Start frontend (in separate terminal)
npm start

# Run database migrations
python -m alembic upgrade head

# Run tests
pytest tests/ -v
npm test
```

### 🎯 Immediate Goals
1. Get both frontend and backend running simultaneously
2. Establish successful database connections
3. Test basic agent functionality through web interface
4. Verify WebSocket real-time communication
5. Validate agent execution with tool integration

## System Overview

This is the LangGraph Deep Web Agent - a comprehensive AI-powered web automation system that combines LangGraph orchestration, LangChain tools, and modern web technologies. The system enables intelligent agents to perform complex web tasks with multi-modal processing, real-time communication, and enterprise-grade security.

## Architecture

### Core Components

**Backend (FastAPI)**
- **Agent Layer**: LangGraph-based orchestration with execution engine and specialized nodes (input, planning, execution, memory, output)
- **API Layer**: RESTful endpoints and WebSocket real-time communication
- **Services**: Authentication, conversation management, tool execution, file handling, caching, rate limiting
- **Security**: JWT authentication, RBAC, data encryption, threat detection, audit logging

**Frontend (React/TypeScript)**
- **UI Components**: Chat interface, dashboard, agent tools, conversation history
- **Real-time**: WebSocket connections for live agent interaction
- **State Management**: Zustand stores with React Query for server state
- **UI Library**: Chakra UI with Material Design components

**Data Layer**
- **PostgreSQL**: Primary database with SQLAlchemy ORM and Alembic migrations
- **Redis**: Caching, session management, rate limiting, and pub/sub
- **Vector Storage**: Pinecone/ChromaDB for semantic search and memory

**Infrastructure**
- **Containerization**: Multi-stage Docker builds with development and production configs
- **Orchestration**: Docker Compose for development, Kubernetes for production
- **CI/CD**: GitHub Actions with comprehensive testing, security scanning, and deployment

## Development Commands

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run database migrations
python -m alembic upgrade head
python -m alembic revision --autogenerate -m "description"

# Run tests
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Code quality
black app/
isort app/
flake8 app/
mypy app/
```

### Frontend Development
```bash
# Install dependencies
cd frontend && npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run linting
npm run lint
npm run type-check

# Run E2E tests
npm run test:e2e
```

### Docker Development
```bash
# Start full development environment
./scripts/dev-start.sh setup
./scripts/dev-start.sh start

# Start local development servers
./scripts/dev-start.sh local

# Run tests in Docker
./scripts/dev-start.sh test

# View logs
./scripts/dev-start.sh logs [service]
```

### Production Deployment
```bash
# Build and deploy
./scripts/deploy.sh build
./scripts/deploy.sh deploy

# Deployment strategies
./scripts/deploy.sh deploy --strategy=blue-green
./scripts/deploy.sh deploy --strategy=canary --traffic=10

# Health checks and monitoring
./scripts/deploy.sh health
./scripts/deploy.sh backup
./scripts/deploy.sh rollback
```

## Key Architectural Patterns

### Agent Orchestration
The system uses LangGraph for agent workflow management with specialized nodes:
- **Input Node**: Processes user input and context
- **Planning Node**: Creates execution plans using LLM reasoning
- **Execution Node**: Executes tools and external APIs
- **Memory Node**: Manages conversation context and user preferences
- **Output Node**: Formats and delivers responses

### Tool Integration
Tools are integrated through LangChain with custom implementations:
- **LangChain Tools**: Web search, document processing, data analysis
- **Custom Tools**: Cloud services, social media, payment systems
- **Multi-modal Tools**: Image processing, file analysis, structured data

### Security Architecture
Multi-layered security approach:
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Encryption at rest and in transit
- **Threat Detection**: Real-time monitoring and alerting
- **Audit Logging**: Comprehensive activity tracking

### Real-time Communication
WebSocket-based architecture for live agent interaction:
- **Connection Management**: Automatic reconnection and session handling
- **Message Routing**: Typed messages with proper serialization
- **Event Handling**: User input, agent responses, system events

## File Structure Conventions

### Backend Structure
```
app/
├── main.py                 # FastAPI application entry point
├── core/                   # Core infrastructure
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection and models
│   └── redis.py           # Redis connection and utilities
├── agents/                 # Agent orchestration
│   ├── agent_orchestrator.py  # Main agent coordinator
│   ├── execution_engine.py     # Task execution logic
│   └── nodes/                 # LangGraph node implementations
├── api/                    # API endpoints
│   ├── endpoints/             # Individual endpoint modules
│   └── dependencies.py         # FastAPI dependencies
├── services/               # Business logic services
├── security/               # Security components
├── tools/                  # Tool integrations
├── integrations/           # External API integrations
└── schemas/                # Pydantic models
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── stores/            # Zustand state stores
│   ├── utils/             # Utility functions
│   └── types/             # TypeScript type definitions
├── public/                # Static assets
└── tests/                 # Test files
```

### Configuration Management
- **Environment Variables**: Use `.env` files for local development
- **Settings Class**: Centralized configuration in `app/core/config.py`
- **Secrets Management**: Never commit secrets; use environment variables
- **Environment-specific**: Separate configs for dev, staging, production

### Database Patterns
- **Models**: SQLAlchemy models in `app/models/`
- **Migrations**: Alembic migrations in `alembic/versions/`
- **Sessions**: Async session management with proper cleanup
- **Relationships**: Clear foreign key relationships with cascading deletes

### API Patterns
- **FastAPI Dependencies**: Use dependency injection for services
- **Pydantic Models**: Strict validation for all API inputs/outputs
- **Error Handling**: Consistent error responses with proper HTTP status codes
- **Pagination**: Standard pagination for list endpoints
- **Rate Limiting**: Redis-based rate limiting with sliding window

## Testing Strategy

### Test Categories
- **Unit Tests**: Individual component testing with mocked dependencies
- **Integration Tests**: Full API testing with real database connections
- **E2E Tests**: Browser-based testing with Playwright
- **Performance Tests**: Load testing with k6 and Locust
- **Security Tests**: Vulnerability scanning with Trivy and OWASP ZAP

### Test Configuration
- **Test Database**: Separate test database with automatic cleanup
- **Test Fixtures**: Pytest fixtures for common test scenarios
- **Mocking**: Use pytest-mock for external dependencies
- **Coverage**: Target 90%+ code coverage

## Development Workflow

### Local Development
1. Use `./scripts/dev-start.sh setup` for initial environment setup
2. Backend runs on `http://localhost:8000` with auto-reload
3. Frontend runs on `http://localhost:3000` with hot reload
4. PostgreSQL on `:5432`, Redis on `:6379`

### Code Quality
- **Linting**: Black for Python, ESLint for TypeScript
- **Type Checking**: MyPy for Python, TypeScript compiler
- **Security**: Bandit for Python, npm audit for dependencies
- **Testing**: Pre-commit hooks for test validation

### Git Workflow
- **Feature Branches**: Create branches for new features
- **Pull Requests**: Required for code review
- **CI/CD**: Automated testing and deployment on push/merge
- **Versioning**: Semantic versioning with git tags

## Performance Considerations

### Backend Optimization
- **Database Connection Pooling**: Configured for high concurrency
- **Redis Caching**: Strategic caching of frequent operations
- **Async Operations**: Non-blocking I/O throughout the application
- **Rate Limiting**: Protect against abuse and resource exhaustion

### Frontend Optimization
- **Code Splitting**: Dynamic imports for large components
- **Virtual Scrolling**: For long lists and chat histories
- **Debouncing**: User input and API calls
- **Image Optimization**: Lazy loading and compression

### Memory Management
- **Agent State**: Proper cleanup of agent execution contexts
- **WebSocket Sessions**: Automatic cleanup of disconnected sessions
- **Database Connections**: Connection pooling with proper disposal
- **File Uploads**: Streaming processing for large files

## Security Guidelines

### Authentication & Authorization
- Use JWT tokens with short expiration and refresh mechanism
- Implement proper RBAC with role hierarchy
- Validate all user inputs and sanitize outputs
- Use HTTPS everywhere with proper certificate management

### Data Protection
- Encrypt sensitive data at rest and in transit
- Implement proper logging without sensitive information
- Use secure cookie settings and CORS policies
- Regular security scanning and vulnerability assessment

### API Security
- Implement rate limiting and request throttling
- Use proper input validation and parameterized queries
- Implement proper error handling without information leakage
- Use API keys for external service authentication

## Common Issues and Solutions

### Database Connection Issues
- Check PostgreSQL and Redis service status
- Verify connection strings and credentials
- Ensure proper migration execution
- Monitor connection pool usage

### Agent Execution Problems
- Check tool availability and permissions
- Verify LLM API keys and rate limits
- Monitor memory usage and execution timeouts
- Review agent state and execution logs

### Frontend WebSocket Issues
- Verify WebSocket server connectivity
- Check authentication token validity
- Monitor message serialization/deserialization
- Implement proper error handling and reconnection

### Performance Bottlenecks
- Profile database queries and add indexes
- Optimize Redis usage and cache strategies
- Monitor agent execution times and tool performance
- Implement proper pagination and lazy loading

## Monitoring and Observability

### Application Metrics
- **Prometheus**: Custom metrics for API performance and agent execution
- **Grafana**: Dashboards for system health and performance
- **Sentry**: Error tracking and performance monitoring
- **Health Checks**: Comprehensive health endpoints for all services

### Logging
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Log Levels**: Appropriate log levels for different environments
- **Log Aggregation**: Centralized logging with ELK stack
- **Audit Logs**: Security-critical events with proper retention

### Alerting
- **Error Rates**: Alert on abnormal error rate increases
- **Response Times**: Alert on slow API responses
- **Resource Usage**: Alert on high CPU/memory/disk usage
- **Security Events**: Alert on security incidents and policy violations