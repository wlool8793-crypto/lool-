#!/usr/bin/env python3
"""
Database initialization script for the Deep Agent application.
"""
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import create_tables, SessionLocal
from app.core.config import settings
from app.services.auth import AuthService
from app.services.user import UserService
from sqlalchemy.orm import Session


def create_superuser():
    """Create a superuser if it doesn't exist."""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        auth_service = AuthService(db)

        # Check if superuser already exists
        superuser = user_service.get_by_email("admin@deepagent.com")
        if superuser:
            print("Superuser already exists!")
            return

        # Create superuser
        superuser = user_service.create(
            user_data={
                "email": "admin@deepagent.com",
                "username": "admin",
                "password": "admin123",  # Change this in production
                "full_name": "Deep Agent Administrator"
            }
        )

        # Hash the password
        hashed_password = auth_service.get_password_hash("admin123")
        superuser.hashed_password = hashed_password
        superuser.is_superuser = True
        superuser.is_active = True

        db.commit()
        print("Superuser created successfully!")
        print("Email: admin@deepagent.com")
        print("Password: admin123")
        print("⚠️  Please change the password in production!")

    except Exception as e:
        print(f"Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()


def create_sample_data():
    """Create sample data for testing."""
    db = SessionLocal()
    try:
        from app.models import Conversation, Message

        # Create sample conversation
        conversation = Conversation(
            user_id=1,  # Assuming superuser has ID 1
            title="Welcome Conversation",
            session_id="welcome_session_001",
            metadata={"type": "welcome", "created_by": "system"}
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Create sample messages
        messages = [
            {
                "conversation_id": conversation.id,
                "role": "assistant",
                "content": "Welcome to Deep Agent! I'm your AI assistant powered by LangGraph. How can I help you today?",
                "message_type": "text",
                "metadata": {"type": "greeting"}
            },
            {
                "conversation_id": conversation.id,
                "role": "user",
                "content": "Hello! I'd like to learn more about what you can do.",
                "message_type": "text",
                "metadata": {"type": "inquiry"}
            }
        ]

        for msg_data in messages:
            message = Message(**msg_data)
            db.add(message)

        db.commit()
        print("Sample data created successfully!")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function to initialize the database."""
    print("🚀 Initializing Deep Agent Database...")

    # Create database tables
    print("📋 Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return

    # Create superuser
    print("👤 Creating superuser...")
    create_superuser()

    # Create sample data
    print("📝 Creating sample data...")
    create_sample_data()

    print("🎉 Database initialization completed!")
    print("\nNext steps:")
    print("1. Set up your .env file with database credentials")
    print("2. Run the application: python -m uvicorn app.main:app --reload")
    print("3. Access the API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    main()