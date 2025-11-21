"""
Constants Module for IndianKanoon Scraper
All magic numbers and constant values are defined here for easy configuration and maintenance.
"""

# ============================================================================
# RATE LIMITING AND TIMING
# ============================================================================

# Default delay between requests (seconds)
DEFAULT_DELAY_SECONDS = 2

# Multiplier for retry delays (exponential backoff)
RETRY_DELAY_MULTIPLIER = 2

# Maximum number of retry attempts for failed requests
MAX_RETRY_ATTEMPTS = 3

# Delay for exponential backoff base (seconds)
EXPONENTIAL_BACKOFF_BASE = 0.5


# ============================================================================
# PDF VALIDATION
# ============================================================================

# Minimum valid PDF file size (bytes)
MIN_PDF_SIZE_BYTES = 1024

# PDF file header signature for validation
PDF_HEADER_SIGNATURE = b'%PDF'

# Number of bytes to read for PDF header validation
PDF_HEADER_READ_BYTES = 4


# ============================================================================
# BATCHING AND PAGINATION
# ============================================================================

# Default batch size for bulk operations
DEFAULT_BATCH_SIZE = 50

# Maximum number of concurrent workers for parallel processing
# Updated to 100 to support 100 proxy IPs (1:1 worker-to-proxy ratio)
MAX_CONCURRENT_WORKERS = 100

# Default number of workers (conservative for systems without proxies)
DEFAULT_WORKERS = 20

# Default limit for database queries
DEFAULT_DB_QUERY_LIMIT = 100

# Default limit for URL tracker queries
DEFAULT_URL_TRACKER_LIMIT = 1000


# ============================================================================
# TIMEOUTS
# ============================================================================

# Standard HTTP request timeout (seconds)
REQUEST_TIMEOUT_SECONDS = 90

# PDF download timeout for large files (seconds)
PDF_DOWNLOAD_TIMEOUT_SECONDS = 120

# General request timeout (seconds)
GENERAL_REQUEST_TIMEOUT = 10


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Default database connection pool size
DEFAULT_POOL_SIZE = 5

# Maximum overflow connections beyond pool size
MAX_POOL_OVERFLOW = 10

# Pool timeout in seconds
POOL_TIMEOUT_SECONDS = 30

# Connection recycle time (seconds) - 1 hour
POOL_RECYCLE_SECONDS = 3600


# ============================================================================
# CHECKPOINTS AND PROGRESS TRACKING
# ============================================================================

# Number of documents between progress saves
CHECKPOINT_INTERVAL = 100

# Heartbeat/monitoring interval (seconds)
HEARTBEAT_INTERVAL = 60

# Report generation interval (number of documents)
REPORT_GENERATION_INTERVAL = 1000

# Checkpoint save interval (number of documents)
CHECKPOINT_SAVE_INTERVAL = 500


# ============================================================================
# FILE I/O
# ============================================================================

# Chunk size for streaming downloads (bytes)
DOWNLOAD_CHUNK_SIZE = 8192

# Buffer size for file operations
FILE_BUFFER_SIZE = 8192


# ============================================================================
# SCRAPER DEFAULTS
# ============================================================================

# Default maximum pages to scrape per query
DEFAULT_MAX_PAGES = 10

# Default results per page
DEFAULT_RESULTS_PER_PAGE = 10

# Maximum pagination depth to check
MAX_PAGINATION_CHECK = 100


# ============================================================================
# BROWSER/SELENIUM CONFIGURATION
# ============================================================================

# Default window size for headless browser
DEFAULT_WINDOW_WIDTH = 1920
DEFAULT_WINDOW_HEIGHT = 1080


# ============================================================================
# TIER CONFIGURATION
# ============================================================================

# Default scrape tier
DEFAULT_SCRAPE_TIER = 1

# Available tiers
TIER_PRIORITY = 1
TIER_HIGH = 2
TIER_MEDIUM = 3
TIER_COMPLETE = 4


# ============================================================================
# PROXY CONFIGURATION
# ============================================================================

# Maximum consecutive proxy failures before disabling
MAX_PROXY_CONSECUTIVE_FAILURES = 5

# Proxy health check interval (seconds)
PROXY_HEALTH_CHECK_INTERVAL = 300

# Default proxy rotation strategy
DEFAULT_PROXY_ROTATION = "round_robin"  # Options: round_robin, least_used, best_performing

# Request delay when using proxies (can be more aggressive)
PROXY_REQUEST_DELAY = 0.5

# Maximum requests per second per proxy (conservative)
MAX_REQUESTS_PER_PROXY_PER_SECOND = 2.0


# ============================================================================
# STORAGE LIMITS
# ============================================================================

# Maximum disk space usage (GB)
MAX_DISK_SPACE_GB = 500

# Minimum free space required (GB)
MIN_FREE_SPACE_GB = 50


# ============================================================================
# ERROR HANDLING
# ============================================================================

# Maximum retry attempts before skipping
MAX_RETRIES_BEFORE_SKIP = 5

# Maximum download attempts for URL tracker
MAX_DOWNLOAD_ATTEMPTS = 3


# ============================================================================
# PARALLEL PROCESSING
# ============================================================================

# Number of courts to process in parallel
PARALLEL_COURTS = 3

# Number of years to process per court in parallel
PARALLEL_YEARS = 2


# ============================================================================
# YEAR RANGES
# ============================================================================

# Default start year for scraping
DEFAULT_START_YEAR = 2020

# Default end year for scraping
DEFAULT_END_YEAR = 2024

# Historical scraping start year
HISTORICAL_START_YEAR = 1950

# Historical scraping end year
HISTORICAL_END_YEAR = 2014

# Historical batch size (years at a time)
HISTORICAL_BATCH_YEARS = 5


# ============================================================================
# QUERY OPTIMIZATION
# ============================================================================

# Query result caching TTL (seconds)
CACHE_TTL_SECONDS = 300  # 5 minutes

# Maximum number of cached queries
CACHE_MAX_SIZE = 128

# Slow query threshold for logging (seconds)
SLOW_QUERY_THRESHOLD_SECONDS = 1.0

# Yield per batch size for memory-efficient queries
QUERY_YIELD_PER_SIZE = 100


# ============================================================================
# RATE LIMITER CONFIGURATION
# ============================================================================

# Maximum requests per second
DEFAULT_MAX_REQUESTS_PER_SECOND = 10.0
CONSERVATIVE_MAX_REQUESTS_PER_SECOND = 5.0
AGGRESSIVE_MAX_REQUESTS_PER_SECOND = 20.0
