"""
Monitoring and logging utilities for Neo4j Legal Knowledge Graph

Provides structured logging, performance metrics, and monitoring capabilities
"""
import time
import functools
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from loguru import logger
import json

# Configure loguru logger
def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week"
):
    """
    Configure structured logging with loguru

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        rotation: Log rotation size
        retention: Log retention period

    Example:
        setup_logging(log_level="INFO", log_file="logs/app.log")
    """
    # Remove default logger
    logger.remove()

    # Console logging with color
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # File logging if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            sink=log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            serialize=False
        )

        logger.info(f"Logging to file: {log_file}")


class PerformanceMonitor:
    """
    Monitor and track performance metrics

    Example:
        monitor = PerformanceMonitor()

        with monitor.track("operation_name"):
            # Your code here
            pass

        metrics = monitor.get_metrics()
        monitor.export_metrics("metrics.json")
    """

    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.start_time = datetime.now()

    def track(self, operation_name: str):
        """
        Context manager for tracking operation time

        Args:
            operation_name: Name of operation to track

        Example:
            with monitor.track("neo4j_query"):
                session.run(query)
        """
        return OperationTracker(self, operation_name)

    def record(self, operation_name: str, duration_ms: float, metadata: Dict = None):
        """
        Record performance metric

        Args:
            operation_name: Operation name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        """
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []

        record = {
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }

        self.metrics[operation_name].append(record)

        # Log slow operations
        if duration_ms > 1000:  # > 1 second
            logger.warning(
                f"Slow operation: {operation_name} took {duration_ms:.2f}ms",
                extra=metadata
            )

    def get_metrics(self, operation_name: Optional[str] = None) -> Dict:
        """
        Get performance metrics

        Args:
            operation_name: Specific operation (or all if None)

        Returns:
            Dictionary of metrics
        """
        if operation_name:
            return self.metrics.get(operation_name, [])

        # Calculate statistics for all operations
        stats = {}
        for op_name, records in self.metrics.items():
            if not records:
                continue

            durations = [r["duration_ms"] for r in records]
            stats[op_name] = {
                "count": len(records),
                "total_ms": sum(durations),
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "p50_ms": self._percentile(durations, 50),
                "p95_ms": self._percentile(durations, 95),
                "p99_ms": self._percentile(durations, 99)
            }

        return stats

    def _percentile(self, values: list, percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def export_metrics(self, output_path: str):
        """
        Export metrics to JSON file

        Args:
            output_path: Path to output JSON file
        """
        stats = self.get_metrics()
        runtime_seconds = (datetime.now() - self.start_time).total_seconds()

        export_data = {
            "start_time": self.start_time.isoformat(),
            "export_time": datetime.now().isoformat(),
            "runtime_seconds": runtime_seconds,
            "statistics": stats,
            "raw_metrics": self.metrics
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported metrics to {output_path}")

    def print_summary(self):
        """Print metrics summary to console"""
        stats = self.get_metrics()

        print("\n" + "="*60)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*60)

        for op_name, op_stats in stats.items():
            print(f"\n{op_name}:")
            print(f"  Count: {op_stats['count']}")
            print(f"  Total: {op_stats['total_ms']:.2f}ms")
            print(f"  Avg: {op_stats['avg_ms']:.2f}ms")
            print(f"  Min: {op_stats['min_ms']:.2f}ms")
            print(f"  Max: {op_stats['max_ms']:.2f}ms")
            print(f"  P50: {op_stats['p50_ms']:.2f}ms")
            print(f"  P95: {op_stats['p95_ms']:.2f}ms")
            print(f"  P99: {op_stats['p99_ms']:.2f}ms")

        runtime = (datetime.now() - self.start_time).total_seconds()
        print(f"\nTotal Runtime: {runtime:.2f}s")
        print("="*60 + "\n")


class OperationTracker:
    """Context manager for operation tracking"""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        metadata = {}
        if exc_type:
            metadata["error"] = str(exc_val)
            metadata["error_type"] = exc_type.__name__
            logger.error(
                f"Operation failed: {self.operation_name} ({duration_ms:.2f}ms)",
                exc_info=True
            )
        else:
            logger.debug(f"Completed operation: {self.operation_name} ({duration_ms:.2f}ms)")

        self.monitor.record(self.operation_name, duration_ms, metadata)
        return False  # Don't suppress exceptions


def monitor_function(operation_name: Optional[str] = None):
    """
    Decorator to monitor function performance

    Args:
        operation_name: Optional operation name (uses function name if not provided)

    Example:
        @monitor_function("create_case_node")
        def create_case(session, case_data):
            # Your code
            pass
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                logger.debug(f"{op_name} completed in {duration_ms:.2f}ms")

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                logger.error(
                    f"{op_name} failed after {duration_ms:.2f}ms: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


class Neo4jQueryProfiler:
    """
    Profile Neo4j queries for performance optimization

    Example:
        profiler = Neo4jQueryProfiler(driver)
        results = profiler.profile_query("MATCH (n) RETURN count(n)")
        profiler.print_report()
    """

    def __init__(self, driver):
        self.driver = driver
        self.profiles = []

    def profile_query(self, query: str, parameters: Dict = None, database: str = "neo4j"):
        """
        Profile a Cypher query

        Args:
            query: Cypher query
            parameters: Query parameters
            database: Database name

        Returns:
            Query results
        """
        logger.info(f"Profiling query: {query[:100]}...")

        with self.driver.session(database=database) as session:
            # Run with PROFILE
            profile_query = f"PROFILE {query}"

            start_time = time.time()
            result = session.run(profile_query, parameters or {})

            # Consume results
            records = list(result)
            duration_ms = (time.time() - start_time) * 1000

            # Get profile info
            profile = result.consume().profile

            profile_info = {
                "query": query,
                "parameters": parameters,
                "duration_ms": duration_ms,
                "records_returned": len(records),
                "db_hits": profile.db_hits if profile else None,
                "rows": profile.rows if profile else None
            }

            self.profiles.append(profile_info)

            logger.info(f"Query completed: {duration_ms:.2f}ms, {len(records)} records")

            return records

    def print_report(self):
        """Print profiling report"""
        print("\n" + "="*60)
        print("NEO4J QUERY PROFILING REPORT")
        print("="*60)

        for idx, profile in enumerate(self.profiles, 1):
            print(f"\nQuery {idx}:")
            print(f"  Query: {profile['query'][:100]}...")
            print(f"  Duration: {profile['duration_ms']:.2f}ms")
            print(f"  Records: {profile['records_returned']}")
            if profile['db_hits']:
                print(f"  DB Hits: {profile['db_hits']}")

        print("="*60 + "\n")


# Global performance monitor instance
global_monitor = PerformanceMonitor()


# Convenience function to setup logging
def init_monitoring(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Initialize monitoring and logging

    Args:
        log_level: Log level
        log_file: Optional log file path

    Example:
        from utils.monitoring import init_monitoring
        init_monitoring(log_level="INFO", log_file="logs/app.log")
    """
    setup_logging(log_level=log_level, log_file=log_file)
    logger.info("Monitoring initialized")
