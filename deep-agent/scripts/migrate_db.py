#!/usr/bin/env python3
"""
Database migration script for the Deep Agent application.
"""
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config


def run_migration(message="Auto migration"):
    """Run database migration."""
    print("🔄 Running database migration...")

    try:
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")

        # Generate migration
        command.revision(alembic_cfg, autogenerate=True, message=message)

        # Run upgrade
        command.upgrade(alembic_cfg, "head")

        print("✅ Database migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False


def rollback_migration(revision):
    """Rollback database to specific revision."""
    print(f"🔄 Rolling back database to revision {revision}...")

    try:
        alembic_cfg = Config("alembic.ini")
        command.downgrade(alembic_cfg, revision)
        print(f"✅ Database rollback to revision {revision} completed!")
        return True

    except Exception as e:
        print(f"❌ Error rolling back database: {e}")
        return False


def show_current_revision():
    """Show current database revision."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.current(alembic_cfg, verbose=True)
        return True

    except Exception as e:
        print(f"❌ Error showing current revision: {e}")
        return False


def show_history():
    """Show migration history."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.history(alembic_cfg, verbose=True)
        return True

    except Exception as e:
        print(f"❌ Error showing history: {e}")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Database migration utility")
    parser.add_argument("action", choices=["migrate", "rollback", "current", "history"],
                       help="Action to perform")
    parser.add_argument("--message", default="Auto migration",
                       help="Migration message (for migrate action)")
    parser.add_argument("--revision", help="Target revision (for rollback action)")

    args = parser.parse_args()

    if args.action == "migrate":
        run_migration(args.message)
    elif args.action == "rollback":
        if not args.revision:
            print("❌ --revision is required for rollback action")
            sys.exit(1)
        rollback_migration(args.revision)
    elif args.action == "current":
        show_current_revision()
    elif args.action == "history":
        show_history()


if __name__ == "__main__":
    main()