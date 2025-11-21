# Complete Project Improvement Implementation Plan

**Project:** IndianKanoon Data Collection System
**Date Created:** October 20, 2025
**Status:** Phase 1 Started (2/60 tasks complete)
**Estimated Completion:** 4 weeks (60 tasks total)

---

## Executive Summary

This document outlines ALL improvements needed to transform the IndianKanoon scraper from a prototype into a **production-ready, enterprise-grade legal data collection system** capable of handling 500,000+ documents reliably.

### Current State
- ✅ 600 cases collected
- ✅ 74 cases with full text
- ✅ 22 PDFs downloaded
- ⚠️ Security vulnerabilities present
- ⚠️ Memory leaks in Selenium
- ⚠️ SQLite not scalable for 500K records
- ⚠️ Sequential downloads (slow)
- ⚠️ No tests, monitoring, or proper error handling

### Target State
- ✅ 500,000+ cases in PostgreSQL
- ✅ Zero security vulnerabilities
- ✅ 10x faster downloads (300 PDFs/min vs 30/min)
- ✅ 99.9% uptime with auto-restart
- ✅ 80%+ test coverage
- ✅ Real-time monitoring dashboard
- ✅ Full observability and metrics

---

## Identified Issues (60+ Total)

### 🔴 Critical (P0) - 8 Issues
1. **Security**: Google Drive credentials in git
2. **Security**: Incomplete/weak User-Agent string
3. **Memory**: Selenium driver leaks
4. **Memory**: Database session leaks
5. **Performance**: Sequential PDF downloads (not using workers)
6. **Performance**: No database indexes on critical fields
7. **Scalability**: SQLite can't handle 500K records
8. **Reliability**: Generic exception catching masks errors

### 🟠 Important (P1) - 22 Issues
9. Database connection pooling not configured
10. Boolean comparisons use `==` instead of `is`
11. String comparisons use `!= ''` instead of `IS NOT NULL`
12. No retry logic for database operations
13. Large result sets loaded entirely in memory
14. No query result caching
15. No request deduplication
16. Resume requires manual `--start-from` parameter
17. No automatic checkpoint system
18. No health checks or heartbeat monitoring
19. No database backup system
20. PDF download logic duplicated in 3 files
21. Database connection logic duplicated
22. Logging setup duplicated across files
23. Magic numbers everywhere (no constants)
24. Inconsistent type hints
25. No service layer (tight coupling)
26. Monolithic scraper class (398 lines)
27. Missing dependencies: tqdm, PyYAML, google-api-python-client
28. Unused dependency: pymongo
29. Unpinned dependency versions
30. Multiple config files (confusing)

### 🟡 Nice-to-Have (P2) - 15 Issues
31. No structured logging (JSON)
32. No correlation IDs for request tracking
33. No Prometheus metrics
34. No Grafana dashboards
35. No alerting system
36. Dashboard planned but not implemented
37. No unit tests (test files incomplete)
38. No integration tests
39. No CI/CD pipeline
40. No validation of scraped data
41. PDF corruption not detected
42. No schema validation
43. 11 documentation files (excessive)
44. Outdated/contradictory documentation
45. Examples don't work

### 🟢 Optional (P3) - 15 Issues
46. No API documentation (Sphinx)
47. Inconsistent docstrings
48. No pre-commit hooks
49. No code linting configuration
50. No code formatting (Black/isort)
51. No security scanning (bandit)
52. No dependency vulnerability scanning
53. No Docker support
54. No docker-compose for development
55. No deployment documentation
56. No troubleshooting guide
57. No performance profiling
58. No load testing
59. No disaster recovery plan
60. No data retention policy

---

## Implementation Plan (4 Weeks)

## ✅ Phase 1: Critical Security & Infrastructure (Week 1)

### 1.1 Security Fixes ✅ COMPLETED (2/4)
- [x] **Task 1**: Add credentials to .gitignore ✅ DONE
- [x] **Task 2**: Fix User-Agent string with complete headers ✅ DONE
- [ ] **Task 3**: Add security headers to all HTTP requests
- [ ] **Task 4**: Review and secure all sensitive data handling

**Files Modified:**
- `.gitignore` - Added credentials.json, token.pickle
- `src/scraper.py` - Fixed User-Agent with full browser headers

---

### 1.2 Memory Leak Fixes (4 tasks)
- [ ] **Task 5**: Fix Selenium driver cleanup with proper __exit__ method
- [ ] **Task 6**: Add try-finally blocks for driver cleanup
- [ ] **Task 7**: Fix database session leaks in CaseDatabase
- [ ] **Task 8**: Add resource cleanup in download_manager.py

**Expected Changes:**
```python
# src/scraper.py - BEFORE
class IndianKanoonScraper:
    def close_driver(self):
        if self.driver:
            self.driver.quit()

# src/scraper.py - AFTER
class IndianKanoonScraper:
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
        finally:
            self.driver = None
```

---

### 1.3 PostgreSQL Migration (7 tasks)
- [ ] **Task 9**: Add PostgreSQL dependencies
  - Add `psycopg2-binary>=2.9.9` to requirements.txt
  - Add `alembic>=1.13.0` for migrations

- [ ] **Task 10**: Install PostgreSQL locally or use Docker
  ```bash
  # Option 1: Local installation
  sudo apt-get install postgresql postgresql-contrib

  # Option 2: Docker
  docker run --name indiankanoon-postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres:15
  ```

- [ ] **Task 11**: Create PostgreSQL database schema
  ```sql
  CREATE DATABASE indiankanoon;
  CREATE USER indiankanoon_user WITH PASSWORD 'secure_password';
  GRANT ALL PRIVILEGES ON DATABASE indiankanoon TO indiankanoon_user;
  ```

- [ ] **Task 12**: Update `src/database.py` for PostgreSQL support
  - Add connection pooling: `pool_size=10, max_overflow=20`
  - Add pool pre-ping for health checks
  - Support both SQLite and PostgreSQL via environment variable

- [ ] **Task 13**: Create Alembic migration scripts
  - Initialize Alembic: `alembic init migrations`
  - Create initial migration with current schema

- [ ] **Task 14**: Create migration script for existing data
  ```python
  # scripts/migrate_to_postgresql.py
  - Read all 600 cases from SQLite
  - Insert into PostgreSQL in batches of 100
  - Verify data integrity
  - Create backup before migration
  ```

- [ ] **Task 15**: Update `.env` and config files
  ```bash
  # .env - BEFORE
  DATABASE_URL=sqlite:///data/indiankanoon.db

  # .env - AFTER
  DATABASE_URL=postgresql://indiankanoon_user:secure_password@localhost:5432/indiankanoon
  # Fallback for development:
  # DATABASE_URL=sqlite:///data/indiankanoon.db
  ```

**Expected Files:**
- New: `migrations/versions/001_initial_schema.py`
- New: `scripts/migrate_to_postgresql.py`
- Modified: `src/database.py`
- Modified: `requirements.txt`
- Modified: `.env`

---

## Phase 2: Database & Performance Optimization (Week 2)

### 2.1 Database Improvements (8 tasks)
- [ ] **Task 16**: Add missing index on `LegalCase.case_url`
  ```python
  # src/database.py
  __table_args__ = (
      Index('idx_case_url', 'case_url'),  # NEW
      Index('idx_pdf_link', 'pdf_link'),  # NEW
      Index('idx_court_name_year', 'court_name', 'year'),  # NEW
      Index('idx_court_year', 'court_type', 'year'),  # EXISTING
      ...
  )
  ```

- [ ] **Task 17**: Fix boolean comparisons throughout codebase
  ```python
  # BEFORE
  LegalCase.pdf_downloaded == False

  # AFTER
  LegalCase.pdf_downloaded.is_(False)
  ```

- [ ] **Task 18**: Fix string NULL comparisons
  ```python
  # BEFORE
  LegalCase.pdf_link != ''

  # AFTER
  LegalCase.pdf_link.isnot(None) & (LegalCase.pdf_link != '')
  ```

- [ ] **Task 19**: Add database retry decorator
  ```python
  # src/database.py - NEW
  def with_retry(max_attempts=3, backoff_factor=2):
      def decorator(func):
          def wrapper(*args, **kwargs):
              for attempt in range(max_attempts):
                  try:
                      return func(*args, **kwargs)
                  except (OperationalError, DatabaseError) as e:
                      if attempt == max_attempts - 1:
                          raise
                      time.sleep(backoff_factor ** attempt)
          return wrapper
      return decorator
  ```

- [ ] **Task 20**: Add connection health checks
- [ ] **Task 21**: Implement automatic database backup system
  - Daily backups to `data/backups/`
  - Upload backups to Google Drive
  - Keep last 7 days of backups
  - Compression with gzip

- [ ] **Task 22**: Add connection pooling configuration
  ```python
  # src/database.py
  self.engine = create_engine(
      connection_string,
      poolclass=QueuePool,
      pool_size=10,
      max_overflow=20,
      pool_timeout=30,
      pool_pre_ping=True,  # Health check before using connection
      pool_recycle=3600,   # Recycle connections after 1 hour
  )
  ```

- [ ] **Task 23**: Add slow query logging

**Expected Files:**
- Modified: `src/database.py`
- New: `src/database_backup.py`
- New: `scripts/backup_database.sh`

---

### 2.2 Query Optimization (5 tasks)
- [ ] **Task 24**: Replace `.all()` with cursor-based pagination
  ```python
  # BEFORE
  cases = db.session.query(LegalCase).limit(1000).all()  # Loads all in memory

  # AFTER
  query = db.session.query(LegalCase)
  for case in query.yield_per(100):  # Streams 100 at a time
      process_case(case)
  ```

- [ ] **Task 25**: Add query result caching with TTL
  ```python
  from functools import lru_cache

  @lru_cache(maxsize=128)
  def get_cases_by_court(court_name):
      return db.session.query(LegalCase).filter_by(court_name=court_name).all()
  ```

- [ ] **Task 26**: Add database query profiling
- [ ] **Task 27**: Implement slow query logging (queries > 1 second)
- [ ] **Task 28**: Add EXPLAIN ANALYZE for complex queries

---

### 2.3 Concurrent Processing (4 tasks)
- [ ] **Task 29**: Refactor `bulk_download.py` to use ThreadPoolExecutor
  ```python
  # BEFORE: Sequential downloads
  for case in cases:
      download_pdf(case)  # One at a time

  # AFTER: Concurrent downloads
  with ThreadPoolExecutor(max_workers=20) as executor:
      futures = [executor.submit(download_pdf, case) for case in cases]
      for future in as_completed(futures):
          result = future.result()
  ```

- [ ] **Task 30**: Increase worker count from 10 to 20 threads
- [ ] **Task 31**: Add request deduplication using URL hash
- [ ] **Task 32**: Implement download queue with priority (Supreme Court = priority 1)

**Expected Files:**
- Modified: `bulk_download.py` (major refactor)
- New: `src/download_queue.py`

---

## Phase 3: Error Handling & Reliability (Week 2 continued)

### 3.1 Custom Exceptions (5 tasks)
- [ ] **Task 33**: Create custom exception classes
  ```python
  # src/exceptions.py - NEW FILE
  class ScraperException(Exception):
      """Base exception for scraper errors"""
      pass

  class PDFDownloadException(ScraperException):
      """PDF download failed after retries"""
      pass

  class DatabaseException(ScraperException):
      """Database operation failed"""
      pass

  class NetworkException(ScraperException):
      """Network request failed"""
      pass

  class ValidationException(ScraperException):
      """Data validation failed"""
      pass
  ```

- [ ] **Task 34**: Replace all `except Exception` with specific exceptions
- [ ] **Task 35**: Add exception context and stack traces
- [ ] **Task 36**: Add exception monitoring/alerting
- [ ] **Task 37**: Create exception handling middleware

**Expected Files:**
- New: `src/exceptions.py`
- Modified: `src/scraper.py` (10+ locations)
- Modified: `src/database.py` (8+ locations)
- Modified: `bulk_download.py` (5+ locations)

---

### 3.2 Auto-Resume System (4 tasks)
- [ ] **Task 38**: Create checkpoint table in database
  ```sql
  CREATE TABLE checkpoints (
      id SERIAL PRIMARY KEY,
      process_name VARCHAR(100),
      last_case_id INTEGER,
      last_offset INTEGER,
      created_at TIMESTAMP DEFAULT NOW(),
      status VARCHAR(20)
  );
  ```

- [ ] **Task 39**: Save checkpoint every 100 cases
- [ ] **Task 40**: Auto-detect last checkpoint on startup
- [ ] **Task 41**: Remove manual `--start-from` parameter requirement

**Expected Files:**
- Modified: `src/database.py` (add Checkpoint model)
- Modified: `bulk_download.py` (add checkpoint logic)
- New: `src/checkpoint_manager.py`

---

### 3.3 Health Monitoring (3 tasks)
- [ ] **Task 42**: Add heartbeat logging (every 60 seconds)
  ```python
  # Every 60 seconds log:
  logger.info("HEARTBEAT", extra={
      "cases_processed": 150,
      "success_rate": 0.98,
      "queue_depth": 50,
      "uptime_seconds": 3600
  })
  ```

- [ ] **Task 43**: Implement watchdog timer for stuck processes
- [ ] **Task 44**: Add automatic restart on failure

**Expected Files:**
- New: `src/health_monitor.py`
- Modified: `bulk_download.py`

---

## Phase 4: Code Quality & Refactoring (Week 3)

### 4.1 Remove Code Duplication (6 tasks)
- [ ] **Task 45**: Extract PDF download to single function
  - Current: Duplicated in `main.py`, `bulk_download.py`, `download_manager.py`
  - Target: Single function in `src/pdf_downloader.py`

- [ ] **Task 46**: Consolidate database connection logic
- [ ] **Task 47**: Create shared logging setup function
- [ ] **Task 48**: Unify configuration loading
- [ ] **Task 49**: Extract common validation logic
- [ ] **Task 50**: Create shared retry logic decorator

**Expected Files:**
- New: `src/pdf_downloader.py`
- New: `src/config_loader.py`
- New: `src/logging_config.py`
- New: `src/validators.py`
- New: `src/decorators.py`

---

### 4.2 Constants & Configuration (4 tasks)
- [ ] **Task 51**: Create constants file
  ```python
  # src/constants.py - NEW FILE
  # Rate limiting
  DEFAULT_DELAY_SECONDS = 2
  RETRY_DELAY_MULTIPLIER = 2
  MAX_RETRY_ATTEMPTS = 3

  # PDF validation
  MIN_PDF_SIZE_BYTES = 1024
  PDF_HEADER_SIGNATURE = b'%PDF'

  # Batching
  DEFAULT_BATCH_SIZE = 50
  MAX_CONCURRENT_WORKERS = 20

  # Timeouts
  REQUEST_TIMEOUT_SECONDS = 90
  PDF_DOWNLOAD_TIMEOUT_SECONDS = 120

  # Database
  DEFAULT_POOL_SIZE = 10
  MAX_POOL_OVERFLOW = 20
  POOL_TIMEOUT_SECONDS = 30

  # Checkpoints
  CHECKPOINT_INTERVAL = 100  # Save every N cases
  HEARTBEAT_INTERVAL = 60    # Log every N seconds
  ```

- [ ] **Task 52**: Replace all magic numbers with named constants
- [ ] **Task 53**: Create configuration validation schema
- [ ] **Task 54**: Consolidate config files (.env + config.yaml)

**Expected Files:**
- New: `src/constants.py`
- New: `src/config_schema.py`
- Modified: 20+ files to use constants

---

### 4.3 Type Hints (3 tasks)
- [ ] **Task 55**: Add complete type annotations to all functions
  ```python
  # BEFORE
  def save_case(self, case_data):
      return case.id

  # AFTER
  def save_case(self, case_data: Dict[str, Any]) -> Optional[int]:
      return case.id
  ```

- [ ] **Task 56**: Add return type hints consistently
- [ ] **Task 57**: Add mypy configuration
  ```ini
  # mypy.ini - NEW FILE
  [mypy]
  python_version = 3.12
  warn_return_any = True
  warn_unused_configs = True
  disallow_untyped_defs = True
  ```

**Expected Files:**
- New: `mypy.ini`
- Modified: ALL `.py` files in `src/`

---

### 4.4 Code Organization (Refactor scraper.py) (4 tasks)
- [ ] **Task 58**: Split scraper.py into separate modules
  ```
  src/scraper.py (398 lines) → Split into:

  scraper/
  ├── http_client.py       # HTTP requests, session management
  ├── parser.py            # HTML parsing with BeautifulSoup
  ├── pdf_downloader.py    # PDF download logic
  └── selenium_manager.py  # Browser automation
  ```

- [ ] **Task 59**: Create service layer
  ```python
  # src/services/scraper_service.py - NEW
  class ScraperService:
      def __init__(self, db: CaseDatabase, scraper: IndianKanoonScraper):
          self.db = db
          self.scraper = scraper

      def scrape_and_save(self, query: str, year: int) -> Dict:
          # Business logic here
          pass
  ```

- [ ] **Task 60**: Implement repository pattern for database
- [ ] **Task 61**: Add dependency injection

**Expected Files:**
- New: `src/scraper/http_client.py`
- New: `src/scraper/parser.py`
- New: `src/scraper/pdf_downloader.py`
- New: `src/scraper/selenium_manager.py`
- New: `src/services/scraper_service.py`
- New: `src/repositories/case_repository.py`
- Modified: `src/scraper.py` (major refactor)

---

## Phase 5: Dependencies & Configuration (Week 3 continued)

### 5.1 Fix Dependencies (5 tasks)
- [ ] **Task 62**: Remove unused `pymongo` dependency
- [ ] **Task 63**: Add missing dependencies
  ```python
  # requirements.txt - ADD
  tqdm>=4.66.0
  PyYAML>=6.0.1
  google-api-python-client>=2.100.0
  google-auth-oauthlib>=1.1.0
  google-auth-httplib2>=0.1.1
  alembic>=1.13.0
  psycopg2-binary>=2.9.9
  ```

- [ ] **Task 64**: Pin all versions for security
  ```python
  # requirements.txt - CHANGE FROM
  requests>=2.31.0

  # TO
  requests==2.31.0
  ```

- [ ] **Task 65**: Create `requirements-dev.txt`
  ```python
  # requirements-dev.txt - NEW
  pytest>=7.4.0
  pytest-cov>=4.1.0
  black>=23.9.0
  isort>=5.12.0
  flake8>=6.1.0
  mypy>=1.5.0
  bandit>=1.7.5
  ```

- [ ] **Task 66**: Create `requirements-test.txt`

**Expected Files:**
- Modified: `requirements.txt`
- New: `requirements-dev.txt`
- New: `requirements-test.txt`
- New: `requirements-production.txt` (updated)

---

### 5.2 Configuration Cleanup (3 tasks)
- [ ] **Task 67**: Remove unused config options from config.yaml
  - Remove: `district_courts` (not implemented)
  - Remove: `dashboard_enabled` (not implemented yet)
  - Remove: unused tribunal configurations

- [ ] **Task 68**: Add config validation on startup
- [ ] **Task 69**: Document all configuration options in README

---

## Phase 6: Testing Infrastructure (Week 4)

### 6.1 Unit Tests (8 tasks)
- [ ] **Task 70**: Write tests for `src/scraper.py`
  ```python
  # tests/test_scraper.py
  def test_search_cases_returns_results():
      scraper = IndianKanoonScraper()
      results = scraper.search_cases("test", year=2023)
      assert len(results) > 0
      assert 'title' in results[0]

  def test_pdf_download_with_valid_url():
      # Test successful download
      pass

  def test_pdf_download_with_invalid_url():
      # Test error handling
      pass
  ```

- [ ] **Task 71**: Write tests for `src/database.py` (all CRUD)
- [ ] **Task 72**: Write tests for `download_manager.py`
- [ ] **Task 73**: Write tests for `drive_manager.py` with mocked API
- [ ] **Task 74**: Add pytest fixtures for test data
- [ ] **Task 75**: Set up code coverage reporting
  ```bash
  pytest --cov=src --cov-report=html
  ```

- [ ] **Task 76**: Achieve 80%+ test coverage
- [ ] **Task 77**: Add test data fixtures

**Expected Files:**
- New: `tests/test_scraper.py` (comprehensive)
- New: `tests/test_database.py`
- New: `tests/test_download_manager.py`
- New: `tests/test_drive_manager.py`
- New: `tests/fixtures.py`
- New: `pytest.ini`

---

### 6.2 Integration Tests (3 tasks)
- [ ] **Task 78**: Test full scraping workflow end-to-end
- [ ] **Task 79**: Test database migration SQLite → PostgreSQL
- [ ] **Task 80**: Test resume functionality

**Expected Files:**
- New: `tests/integration/test_full_workflow.py`
- New: `tests/integration/test_migration.py`
- New: `tests/integration/test_resume.py`

---

### 6.3 CI/CD Pipeline (4 tasks)
- [ ] **Task 81**: Create GitHub Actions workflow
  ```yaml
  # .github/workflows/test.yml - NEW
  name: Tests
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.12'
        - name: Install dependencies
          run: pip install -r requirements-dev.txt
        - name: Run tests
          run: pytest --cov=src
        - name: Run linters
          run: |
            black --check src/
            isort --check src/
            flake8 src/
        - name: Security scan
          run: bandit -r src/
  ```

- [ ] **Task 82**: Add pre-commit hooks
  ```yaml
  # .pre-commit-config.yaml - NEW
  repos:
    - repo: https://github.com/psf/black
      rev: 23.9.1
      hooks:
        - id: black
    - repo: https://github.com/pycqa/isort
      rev: 5.12.0
      hooks:
        - id: isort
    - repo: https://github.com/pycqa/flake8
      rev: 6.1.0
      hooks:
        - id: flake8
  ```

- [ ] **Task 83**: Add automated security scanning (bandit)
- [ ] **Task 84**: Create deployment workflow

**Expected Files:**
- New: `.github/workflows/test.yml`
- New: `.github/workflows/deploy.yml`
- New: `.pre-commit-config.yaml`

---

## Phase 7: Monitoring & Observability (Week 4)

### 7.1 Structured Logging (4 tasks)
- [ ] **Task 85**: Replace basic logging with structlog
  ```python
  # BEFORE
  logger.info(f"Downloaded PDF: {filename}")

  # AFTER
  logger.info("pdf_downloaded", filename=filename, size=file_size, duration=elapsed)
  ```

- [ ] **Task 86**: Add JSON log format
- [ ] **Task 87**: Implement correlation IDs
- [ ] **Task 88**: Add contextual logging

**Expected Files:**
- New: `src/logging_config.py`
- Modified: ALL files (update logging calls)

---

### 7.2 Metrics Collection (5 tasks)
- [ ] **Task 89**: Add Prometheus client library
  ```python
  # requirements.txt
  prometheus-client>=0.18.0
  ```

- [ ] **Task 90**: Create metrics endpoint
  ```python
  # src/metrics.py - NEW
  from prometheus_client import Counter, Gauge, Histogram

  download_counter = Counter('pdfs_downloaded_total', 'Total PDFs downloaded')
  error_counter = Counter('download_errors_total', 'Total download errors')
  queue_depth = Gauge('download_queue_depth', 'Current queue depth')
  download_duration = Histogram('download_duration_seconds', 'PDF download duration')
  ```

- [ ] **Task 91**: Track key metrics: download_rate, success_rate, error_rate, queue_depth
- [ ] **Task 92**: Create Grafana dashboard JSON
- [ ] **Task 93**: Add alerting rules

**Expected Files:**
- New: `src/metrics.py`
- New: `monitoring/grafana_dashboard.json`
- New: `monitoring/alert_rules.yml`

---

### 7.3 Progress Dashboard (6 tasks)
- [ ] **Task 94**: Create Flask web application
  ```python
  # dashboard/app.py - NEW
  from flask import Flask, render_template
  from flask_socketio import SocketIO

  app = Flask(__name__)
  socketio = SocketIO(app)

  @app.route('/')
  def index():
      return render_template('dashboard.html')
  ```

- [ ] **Task 95**: Add WebSocket support for real-time updates
- [ ] **Task 96**: Create HTML template with charts
- [ ] **Task 97**: Add pause/resume controls
- [ ] **Task 98**: Add visualization charts (Chart.js)
- [ ] **Task 99**: Deploy dashboard on port 8080

**Expected Files:**
- New: `dashboard/app.py`
- New: `dashboard/templates/dashboard.html`
- New: `dashboard/static/css/style.css`
- New: `dashboard/static/js/dashboard.js`

---

## Phase 8: Documentation & Polish (Week 4)

### 8.1 Documentation (5 tasks)
- [ ] **Task 100**: Update README.md with current architecture
- [ ] **Task 101**: Create API documentation with Sphinx
  ```bash
  sphinx-quickstart docs
  sphinx-apidoc -o docs/source src/
  make html
  ```

- [ ] **Task 102**: Add comprehensive docstrings to all functions
- [ ] **Task 103**: Create troubleshooting guide
- [ ] **Task 104**: Add deployment guide

**Expected Files:**
- Modified: `README.md`
- New: `docs/` directory with Sphinx setup
- New: `TROUBLESHOOTING.md`
- New: `DEPLOYMENT.md`

---

### 8.2 Developer Experience (5 tasks)
- [ ] **Task 105**: Create development setup guide
- [ ] **Task 106**: Add docker-compose.yml
  ```yaml
  # docker-compose.yml - NEW
  version: '3.8'
  services:
    postgres:
      image: postgres:15
      environment:
        POSTGRES_DB: indiankanoon
        POSTGRES_USER: indiankanoon_user
        POSTGRES_PASSWORD: dev_password
      ports:
        - "5432:5432"

    scraper:
      build: .
      depends_on:
        - postgres
      volumes:
        - ./data:/app/data
  ```

- [ ] **Task 107**: Create Dockerfile
- [ ] **Task 108**: Add VSCode/PyCharm configuration
- [ ] **Task 109**: Create Makefile for common tasks
  ```makefile
  # Makefile - NEW
  .PHONY: install test lint format

  install:
  	pip install -r requirements-dev.txt

  test:
  	pytest --cov=src

  lint:
  	flake8 src/
  	mypy src/

  format:
  	black src/
  	isort src/
  ```

**Expected Files:**
- New: `docker-compose.yml`
- New: `Dockerfile`
- New: `.vscode/settings.json`
- New: `Makefile`
- New: `DEVELOPMENT.md`

---

## Progress Tracking

### Completed (2/109 tasks)
- [x] Task 1: Add credentials to .gitignore ✅
- [x] Task 2: Fix User-Agent string ✅

### In Progress (1/109 tasks)
- [ ] Task 5: Fix Selenium memory leaks

### Pending (106/109 tasks)
- See detailed task list above

---

## Success Metrics

### Security
- [ ] 0 credentials in git history
- [ ] 0 vulnerabilities in dependencies
- [ ] All sensitive data encrypted or in .gitignore

### Performance
- [ ] Download rate: 300 PDFs/min (currently ~30/min) = **10x improvement**
- [ ] Database query time < 100ms for common queries
- [ ] Memory usage < 2GB (currently ~1GB but leaking)

### Reliability
- [ ] Uptime: 99.9%
- [ ] Success rate: 98%+
- [ ] Auto-restart on failure within 30 seconds
- [ ] Zero data loss with checkpoints

### Code Quality
- [ ] Test coverage: 80%+
- [ ] Type hint coverage: 100%
- [ ] Linting errors: 0
- [ ] Documentation coverage: 100%

### Scalability
- [ ] PostgreSQL supporting 500,000+ cases
- [ ] Concurrent downloads: 20 workers
- [ ] Response time under load: < 1s

---

## File Change Summary

### Files to Create (38 new files)
1. `src/exceptions.py`
2. `src/constants.py`
3. `src/config_loader.py`
4. `src/logging_config.py`
5. `src/validators.py`
6. `src/decorators.py`
7. `src/pdf_downloader.py`
8. `src/database_backup.py`
9. `src/download_queue.py`
10. `src/checkpoint_manager.py`
11. `src/health_monitor.py`
12. `src/metrics.py`
13. `src/config_schema.py`
14. `src/scraper/http_client.py`
15. `src/scraper/parser.py`
16. `src/scraper/pdf_downloader.py`
17. `src/scraper/selenium_manager.py`
18. `src/services/scraper_service.py`
19. `src/repositories/case_repository.py`
20. `scripts/migrate_to_postgresql.py`
21. `scripts/backup_database.sh`
22. `migrations/versions/001_initial_schema.py`
23. `tests/test_scraper.py`
24. `tests/test_database.py`
25. `tests/test_download_manager.py`
26. `tests/test_drive_manager.py`
27. `tests/fixtures.py`
28. `tests/integration/test_full_workflow.py`
29. `tests/integration/test_migration.py`
30. `tests/integration/test_resume.py`
31. `dashboard/app.py`
32. `dashboard/templates/dashboard.html`
33. `.github/workflows/test.yml`
34. `.github/workflows/deploy.yml`
35. `.pre-commit-config.yaml`
36. `docker-compose.yml`
37. `Dockerfile`
38. `Makefile`

### Files to Modify (25 existing files)
1. `.gitignore` ✅ DONE
2. `src/scraper.py` ✅ DONE (User-Agent), needs more changes
3. `src/database.py`
4. `bulk_download.py`
5. `main.py`
6. `download_manager.py`
7. `drive_manager.py`
8. `requirements.txt`
9. `.env`
10. `config/config.yaml`
11. `README.md`
12. All test files (expand coverage)
13-25. Various support files

### Files to Delete (0 files)
- User requested to keep all files

---

## Risk Assessment

### High Risk Changes
1. **PostgreSQL Migration**: Could lose data if not careful
   - Mitigation: Create full backup before migration
   - Mitigation: Test migration on copy of database first

2. **Refactoring scraper.py**: Could break existing functionality
   - Mitigation: Write tests before refactoring
   - Mitigation: Keep old code in git history

3. **Dependency updates**: Could introduce breaking changes
   - Mitigation: Pin versions
   - Mitigation: Test thoroughly before deployment

### Medium Risk Changes
1. **Concurrent downloads**: Could overwhelm server
   - Mitigation: Start with 5 workers, gradually increase
   - Mitigation: Monitor error rates

2. **Database schema changes**: Could break existing queries
   - Mitigation: Use Alembic migrations
   - Mitigation: Test rollback procedures

### Low Risk Changes
1. Security fixes (.gitignore, headers)
2. Adding constants
3. Adding type hints
4. Documentation updates

---

## Rollback Plan

If anything goes wrong:

1. **Database**: Restore from backup
   ```bash
   pg_restore -d indiankanoon backup_20251020.sql
   ```

2. **Code**: Revert to previous commit
   ```bash
   git revert HEAD
   # or
   git reset --hard <commit-hash>
   ```

3. **Dependencies**: Use requirements.txt from git history
   ```bash
   git checkout HEAD~1 requirements.txt
   pip install -r requirements.txt
   ```

---

## Next Steps

**Tomorrow's Tasks:**
1. Review this plan
2. Ask any questions or request changes
3. Begin implementation of remaining Phase 1 tasks:
   - Task 5-8: Fix memory leaks
   - Task 9-15: PostgreSQL migration
4. Set up development environment

**Questions to Consider:**
- Do you want to run PostgreSQL locally or use Docker?
- Should we implement all 109 tasks or prioritize certain phases?
- Are there any additional features you'd like to add?

---

**Document Version:** 1.0
**Last Updated:** October 20, 2025
**Next Review:** Tomorrow (your review)
**Status:** ✅ Security fixes started, 107 tasks remaining
