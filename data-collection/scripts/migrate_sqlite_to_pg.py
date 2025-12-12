#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script for Phase 4
Migrates existing data from SQLite to PostgreSQL with progress tracking
"""

import sys
import os
from pathlib import Path
from typing import Dict, List
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path is set
try:
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.orm import sessionmaker
    from tqdm import tqdm
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Install with: pip install sqlalchemy tqdm psycopg2-binary")
    sys.exit(1)


class DatabaseMigration:
    """Handles migration from SQLite to PostgreSQL"""

    def __init__(self, sqlite_url: str, postgres_url: str):
        """
        Initialize migration

        Args:
            sqlite_url: SQLite database URL (e.g., sqlite:///data/indiankanoon.db)
            postgres_url: PostgreSQL database URL (e.g., postgresql://user:pass@localhost/db)
        """
        self.sqlite_url = sqlite_url
        self.postgres_url = postgres_url

        # Create engines
        print("Connecting to databases...")
        self.sqlite_engine = create_engine(sqlite_url)
        self.postgres_engine = create_engine(postgres_url)

        # Create sessions
        SqliteSession = sessionmaker(bind=self.sqlite_engine)
        PostgresSession = sessionmaker(bind=self.postgres_engine)

        self.sqlite_session = SqliteSession()
        self.postgres_session = PostgresSession()

        print("✓ Connected to both databases")

    def get_table_list(self) -> List[str]:
        """Get list of tables from SQLite database"""
        inspector = inspect(self.sqlite_engine)
        tables = inspector.get_table_names()
        print(f"\nFound {len(tables)} tables in SQLite database:")
        for table in tables:
            row_count = self.sqlite_session.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar()
            print(f"  - {table}: {row_count:,} rows")
        return tables

    def check_postgres_tables(self) -> Dict[str, int]:
        """Check which tables already exist in PostgreSQL"""
        inspector = inspect(self.postgres_engine)
        existing_tables = inspector.get_table_names()

        table_counts = {}
        if existing_tables:
            print(f"\nExisting tables in PostgreSQL:")
            for table in existing_tables:
                row_count = self.postgres_session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()
                table_counts[table] = row_count
                print(f"  - {table}: {row_count:,} rows")
        else:
            print("\nNo existing tables in PostgreSQL (fresh database)")

        return table_counts

    def migrate_table(self, table_name: str, batch_size: int = 1000) -> int:
        """
        Migrate a single table from SQLite to PostgreSQL

        Args:
            table_name: Name of table to migrate
            batch_size: Number of rows to process per batch

        Returns:
            Number of rows migrated
        """
        print(f"\n{'='*70}")
        print(f"Migrating table: {table_name}")
        print(f"{'='*70}")

        # Get total row count
        total_rows = self.sqlite_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()

        if total_rows == 0:
            print(f"  Table '{table_name}' is empty, skipping...")
            return 0

        print(f"  Total rows: {total_rows:,}")

        # Get column names
        inspector = inspect(self.sqlite_engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        columns_str = ', '.join(columns)

        # Check if table exists in PostgreSQL
        pg_inspector = inspect(self.postgres_engine)
        pg_tables = pg_inspector.get_table_names()

        if table_name not in pg_tables:
            print(f"  ⚠ Table '{table_name}' does not exist in PostgreSQL")
            print(f"  Please run migrations first: scripts/setup_postgres_phase4.sh")
            return 0

        # Ask user if they want to clear existing data
        existing_count = self.postgres_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()

        if existing_count > 0:
            print(f"  ⚠ Table '{table_name}' already has {existing_count:,} rows in PostgreSQL")
            response = input(f"  Clear existing data? (y/N): ").strip().lower()
            if response == 'y':
                print(f"  Clearing existing data from {table_name}...")
                self.postgres_session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                self.postgres_session.commit()
                print(f"  ✓ Cleared")

        # Migrate in batches
        migrated_count = 0
        start_time = time.time()

        with tqdm(total=total_rows, desc=f"  Migrating {table_name}", unit=" rows") as pbar:
            offset = 0
            while offset < total_rows:
                # Fetch batch from SQLite
                query = f"SELECT {columns_str} FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
                rows = self.sqlite_session.execute(text(query)).fetchall()

                if not rows:
                    break

                # Prepare batch insert for PostgreSQL
                # Build placeholders
                placeholders = ', '.join([f":{col}" for col in columns])
                insert_query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """

                # Convert rows to list of dicts
                batch_data = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    batch_data.append(row_dict)

                # Execute batch insert
                try:
                    self.postgres_session.execute(text(insert_query), batch_data)
                    self.postgres_session.commit()
                    migrated_count += len(rows)
                    pbar.update(len(rows))
                except Exception as e:
                    print(f"\n  ✗ Error inserting batch at offset {offset}: {e}")
                    self.postgres_session.rollback()
                    # Try inserting one by one
                    for row_dict in batch_data:
                        try:
                            self.postgres_session.execute(text(insert_query), row_dict)
                            self.postgres_session.commit()
                            migrated_count += 1
                            pbar.update(1)
                        except Exception as row_error:
                            print(f"\n  ✗ Failed to insert row: {row_error}")
                            self.postgres_session.rollback()

                offset += batch_size

        elapsed_time = time.time() - start_time
        print(f"\n  ✓ Migrated {migrated_count:,} rows in {elapsed_time:.2f} seconds")
        print(f"    Rate: {migrated_count/elapsed_time:.0f} rows/sec")

        return migrated_count

    def verify_migration(self, table_name: str) -> bool:
        """Verify that migration was successful"""
        sqlite_count = self.sqlite_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()

        postgres_count = self.postgres_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()

        print(f"\nVerification for {table_name}:")
        print(f"  SQLite:     {sqlite_count:,} rows")
        print(f"  PostgreSQL: {postgres_count:,} rows")

        if sqlite_count == postgres_count:
            print(f"  ✓ Row counts match!")
            return True
        else:
            diff = abs(sqlite_count - postgres_count)
            print(f"  ✗ Mismatch: {diff:,} rows different")
            return False

    def migrate_all(self, skip_tables: List[str] = None) -> Dict[str, int]:
        """
        Migrate all tables from SQLite to PostgreSQL

        Args:
            skip_tables: List of table names to skip

        Returns:
            Dictionary of table_name -> rows_migrated
        """
        skip_tables = skip_tables or []

        # Get table list
        tables = self.get_table_list()

        # Check PostgreSQL state
        self.check_postgres_tables()

        # Migration order (respect foreign key dependencies)
        # Core tables first, then referencing tables
        migration_order = [
            'documents',  # Core table
            'parties',    # References documents
            'judges',     # References documents
            'citations',  # References documents
            'content',    # References documents
            'extraction_metadata',  # References documents
        ]

        # Add any remaining tables not in the order
        for table in tables:
            if table not in migration_order and table not in skip_tables:
                migration_order.append(table)

        # Remove tables that don't exist or should be skipped
        migration_order = [
            t for t in migration_order
            if t in tables and t not in skip_tables
        ]

        print(f"\nMigration order: {', '.join(migration_order)}")

        # Confirm before proceeding
        response = input("\nProceed with migration? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return {}

        # Migrate each table
        results = {}
        total_start_time = time.time()

        for table_name in migration_order:
            migrated_count = self.migrate_table(table_name, batch_size=1000)
            results[table_name] = migrated_count

            # Verify
            self.verify_migration(table_name)

        total_elapsed = time.time() - total_start_time

        # Print summary
        print(f"\n{'='*70}")
        print("MIGRATION COMPLETE")
        print(f"{'='*70}")
        print(f"Total time: {total_elapsed:.2f} seconds ({total_elapsed/60:.1f} minutes)")
        print(f"\nMigrated rows by table:")
        total_migrated = 0
        for table, count in results.items():
            print(f"  {table:30s}: {count:>10,} rows")
            total_migrated += count
        print(f"  {'TOTAL':30s}: {total_migrated:>10,} rows")
        print(f"\nAverage rate: {total_migrated/total_elapsed:.0f} rows/sec")
        print(f"{'='*70}")

        return results

    def close(self):
        """Close database connections"""
        self.sqlite_session.close()
        self.postgres_session.close()
        self.sqlite_engine.dispose()
        self.postgres_engine.dispose()


def main():
    """Main migration script"""
    print("="*70)
    print("SQLite to PostgreSQL Migration - Phase 4")
    print("="*70)
    print()

    # Configuration
    sqlite_path = project_root / "data" / "indiankanoon.db"
    if not sqlite_path.exists():
        # Try production DB
        sqlite_path = project_root / "data" / "indiankanoon_production.db"

    if not sqlite_path.exists():
        print(f"✗ SQLite database not found at: {sqlite_path}")
        print("  Please check the path and try again.")
        sys.exit(1)

    sqlite_url = f"sqlite:///{sqlite_path}"

    # PostgreSQL URL from config
    postgres_url = "postgresql://indiankanoon_user:secure_pass_2024@localhost:5432/indiankanoon"

    print(f"Source (SQLite):      {sqlite_path}")
    print(f"Destination (PostgreSQL): indiankanoon@localhost")
    print()

    # Create migrator
    try:
        migrator = DatabaseMigration(sqlite_url, postgres_url)
    except Exception as e:
        print(f"✗ Failed to connect to databases: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running: sudo service postgresql start")
        print("  2. Database is created: ./scripts/setup_postgres_phase4.sh")
        print("  3. Credentials are correct in the script")
        sys.exit(1)

    try:
        # Run migration
        results = migrator.migrate_all()

        if results:
            print("\n✓ Migration completed successfully!")
            print("\nNext steps:")
            print("  1. Update config/config_production.yaml to use PostgreSQL URL")
            print("  2. Test the scraper with: python bulk_download.py --batch-size 10")
            print("  3. Monitor quality with: SELECT * FROM quality_summary;")
        else:
            print("\n⚠ No tables were migrated.")

    except KeyboardInterrupt:
        print("\n\n⚠ Migration interrupted by user")
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close()
        print("\n✓ Database connections closed")


if __name__ == "__main__":
    main()
