#!/usr/bin/env python3
"""
Database connection testing script for the Deep Agent application.
"""
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import create_tables
import time


def test_postgres_connection():
    """Test PostgreSQL database connection."""
    print("🔍 Testing PostgreSQL connection...")

    try:
        # Create engine
        engine = create_engine(settings.database_url)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connected successfully!")
            print(f"   Version: {version}")

            # Test database exists
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   Database: {db_name}")

        return True

    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def test_redis_connection():
    """Test Redis connection."""
    print("\n🔍 Testing Redis connection...")

    try:
        from app.core.redis import redis_manager

        # Test connection
        if redis_manager.ping():
            print("✅ Redis connected successfully!")

            # Test basic operations
            test_key = "test_connection"
            test_value = {"test": "data", "timestamp": time.time()}

            # Test set and get
            if redis_manager.set(test_key, test_value, ex=60):
                retrieved_value = redis_manager.get(test_key)
                if retrieved_value == test_value:
                    print("✅ Redis read/write operations working!")
                    redis_manager.delete(test_key)
                    return True
                else:
                    print("❌ Redis data integrity check failed")
                    return False
            else:
                print("❌ Redis write operation failed")
                return False
        else:
            print("❌ Redis ping failed")
            return False

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


def test_database_tables():
    """Test database tables exist."""
    print("\n🔍 Testing database tables...")

    try:
        engine = create_engine(settings.database_url)

        # Expected tables
        expected_tables = [
            'users', 'conversations', 'messages', 'agent_states',
            'api_keys', 'tool_executions', 'file_uploads', 'system_logs'
        ]

        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))

            existing_tables = [row[0] for row in result.fetchall()]

            print(f"   Found {len(existing_tables)} tables:")
            for table in existing_tables:
                print(f"   - {table}")

            # Check all expected tables exist
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print("✅ All expected tables found!")
                return True

    except Exception as e:
        print(f"❌ Database table check failed: {e}")
        return False


def test_alembic_migrations():
    """Test Alembic migrations."""
    print("\n🔍 Testing Alembic migrations...")

    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")

        # Check current revision
        print("   Checking current database revision...")
        command.current(alembic_cfg, verbose=True)

        # Check migration history
        print("\n   Migration history:")
        command.history(alembic_cfg, verbose=True)

        print("✅ Alembic migrations working!")
        return True

    except Exception as e:
        print(f"❌ Alembic migration test failed: {e}")
        return False


def main():
    """Main function to test database setup."""
    print("🚀 Deep Agent Database Connection Test")
    print("=" * 50)

    tests = [
        ("PostgreSQL Connection", test_postgres_connection),
        ("Redis Connection", test_redis_connection),
        ("Database Tables", test_database_tables),
        ("Alembic Migrations", test_alembic_migrations),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed!")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All database tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python scripts/init_db.py")
        print("2. Start the application: uvicorn app.main:app --reload")
        print("3. Access the API docs: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check your configuration.")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running on port 5432")
        print("2. Ensure Redis is running on port 6379")
        print("3. Check your .env file configuration")
        print("4. Verify database credentials")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)