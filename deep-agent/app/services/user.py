"""
User service for the Deep Agent application.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import User
from app.schemas.auth import UserCreate, UserUpdate


class UserService:
    """Service for user management."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.password,  # Note: Password should be pre-hashed by auth service
            full_name=user_data.full_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users with pagination."""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def make_superuser(self, user_id: int) -> bool:
        """Grant superuser privileges."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.is_superuser = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def revoke_superuser(self, user_id: int) -> bool:
        """Revoke superuser privileges."""
        user = self.get_by_id(user_id)
        if not user:
            return False

        user.is_superuser = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_user_count(self) -> int:
        """Get total user count."""
        return self.db.query(User).count()

    def get_active_user_count(self) -> int:
        """Get active user count."""
        return self.db.query(User).filter(User.is_active == True).count()

    def get_superuser_count(self) -> int:
        """Get superuser count."""
        return self.db.query(User).filter(User.is_superuser == True).count()

    def search_users(self, query: str, skip: int = 0, limit: int = 50) -> List[User]:
        """Search users by email, username, or full name."""
        search_pattern = f"%{query}%"
        return self.db.query(User).filter(
            (User.email.ilike(search_pattern)) |
            (User.username.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        ).offset(skip).limit(limit).all()