"""
Database Connection Manager for Legal RAG System
PostgreSQL connection pooling with SQLAlchemy 2.0
"""

import os
import logging
from typing import Optional, Generator
from contextlib import contextmanager
from datetime import datetime

import yaml
from sqlalchemy import create_engine, event, text, pool
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration loader."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize database configuration.

        Args:
            config_path: Path to database.yaml config file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'database.yaml'
            )

        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}. Using defaults.")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Get default configuration."""
        return {
            'database': {
                'host': 'localhost',
                'port': 5433,
                'database': 'legal_rag_db',
                'user': 'legal_rag_user',
                'password': 'secure_rag_password_2024',
                'pool': {
                    'pool_size': 10,
                    'max_overflow': 20,
                    'pool_timeout': 30,
                    'pool_recycle': 3600,
                    'pool_pre_ping': True,
                    'echo': False,
                }
            }
        }

    @property
    def url(self) -> str:
        """Get database URL from config or environment."""
        # Check environment variable first
        env_url = os.getenv('DATABASE_URL')
        if env_url:
            return env_url

        # Build from config
        db_config = self.config['database']
        return (
            f"postgresql://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

    @property
    def pool_config(self) -> dict:
        """Get connection pool configuration."""
        return self.config.get('database', {}).get('pool', {})


class DatabaseConnection:
    """
    Database connection manager with connection pooling.

    Features:
    - Connection pooling with configurable size
    - Automatic connection health checks
    - Session management
    - Query logging
    - Slow query detection
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database connection.

        Args:
            config: Database configuration object
        """
        self.config = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.scoped_session_factory: Optional[scoped_session] = None
        self._is_connected = False

    def connect(self) -> None:
        """Establish database connection with pooling."""
        if self._is_connected:
            logger.warning("Already connected to database")
            return

        try:
            pool_config = self.config.pool_config

            # Create engine with connection pooling
            self.engine = create_engine(
                self.config.url,
                poolclass=pool.QueuePool,
                pool_size=pool_config.get('pool_size', 10),
                max_overflow=pool_config.get('max_overflow', 20),
                pool_timeout=pool_config.get('pool_timeout', 30),
                pool_recycle=pool_config.get('pool_recycle', 3600),
                pool_pre_ping=pool_config.get('pool_pre_ping', True),
                echo=pool_config.get('echo', False),
                echo_pool=pool_config.get('echo_pool', False),
                future=True,  # SQLAlchemy 2.0 style
            )

            # Setup event listeners
            self._setup_event_listeners()

            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )

            # Create thread-safe scoped session
            self.scoped_session_factory = scoped_session(self.session_factory)

            # Test connection
            self._test_connection()

            self._is_connected = True
            logger.info(f"Connected to database: {self.engine.url.database}")

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners for monitoring."""
        if not self.engine:
            return

        # Log slow queries
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(datetime.now())

        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = (datetime.now() - conn.info['query_start_time'].pop()).total_seconds()
            if total_time > 1.0:  # Log queries slower than 1 second
                logger.warning(f"Slow query ({total_time:.2f}s): {statement[:200]}")

        # Log connection pool events
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("New database connection established")

        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")

    def _test_connection(self) -> None:
        """Test database connection."""
        if not self.engine:
            raise RuntimeError("Engine not initialized")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    def disconnect(self) -> None:
        """Close all connections and dispose of the engine."""
        if not self._is_connected:
            return

        try:
            if self.scoped_session_factory:
                self.scoped_session_factory.remove()

            if self.engine:
                self.engine.dispose()

            self._is_connected = False
            logger.info("Disconnected from database")

        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
            raise

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy Session instance

        Example:
            >>> db = DatabaseConnection()
            >>> db.connect()
            >>> session = db.get_session()
            >>> # Use session
            >>> session.close()
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to database. Call connect() first.")

        return self.session_factory()

    def get_scoped_session(self) -> scoped_session:
        """
        Get a thread-safe scoped session.

        Returns:
            Scoped session (thread-local)
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to database. Call connect() first.")

        return self.scoped_session_factory

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.

        Yields:
            SQLAlchemy Session

        Example:
            >>> db = DatabaseConnection()
            >>> db.connect()
            >>> with db.session_scope() as session:
            ...     document = session.query(Document).first()
            ...     # Session is automatically committed or rolled back
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def health_check(self) -> dict:
        """
        Perform database health check.

        Returns:
            Dict with health status information
        """
        health = {
            'connected': self._is_connected,
            'timestamp': datetime.now().isoformat(),
        }

        if not self._is_connected:
            health['status'] = 'disconnected'
            return health

        try:
            with self.engine.connect() as conn:
                # Test query
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

                # Get pool status
                pool_status = self.engine.pool.status()
                health['pool_status'] = pool_status

                # Get database size
                result = conn.execute(text(
                    "SELECT pg_size_pretty(pg_database_size(current_database())) as size"
                ))
                health['database_size'] = result.fetchone()[0]

                # Get connection count
                result = conn.execute(text(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                ))
                health['active_connections'] = result.fetchone()[0]

                health['status'] = 'healthy'

        except Exception as e:
            health['status'] = 'unhealthy'
            health['error'] = str(e)
            logger.error(f"Health check failed: {e}")

        return health

    def execute_raw_sql(self, sql: str, params: Optional[dict] = None) -> list:
        """
        Execute raw SQL query.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of result rows
        """
        with self.session_scope() as session:
            result = session.execute(text(sql), params or {})
            return result.fetchall()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db_connection() -> DatabaseConnection:
    """
    Get global database connection instance (singleton).

    Returns:
        DatabaseConnection instance
    """
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
        _db_connection.connect()
    return _db_connection


def init_db(config: Optional[DatabaseConfig] = None) -> DatabaseConnection:
    """
    Initialize database connection.

    Args:
        config: Database configuration

    Returns:
        DatabaseConnection instance
    """
    global _db_connection
    if _db_connection is not None:
        _db_connection.disconnect()

    _db_connection = DatabaseConnection(config)
    _db_connection.connect()
    return _db_connection


def close_db() -> None:
    """Close global database connection."""
    global _db_connection
    if _db_connection is not None:
        _db_connection.disconnect()
        _db_connection = None


if __name__ == "__main__":
    # Test connection
    logging.basicConfig(level=logging.INFO)

    print("Testing database connection...")
    with DatabaseConnection() as db:
        print(f"Connected: {db._is_connected}")

        # Health check
        health = db.health_check()
        print(f"\nHealth Check:")
        for key, value in health.items():
            print(f"  {key}: {value}")

        # Test query
        with db.session_scope() as session:
            result = session.execute(text("SELECT COUNT(*) FROM documents"))
            count = result.scalar()
            print(f"\nDocuments in database: {count}")
