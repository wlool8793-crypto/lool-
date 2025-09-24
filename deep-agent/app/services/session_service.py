import secrets
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from app.services.cache_service import cache_service
from app.core.config import settings
from app.models import User
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """
    Session management service using Redis
    """

    def __init__(self):
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.session_ttl = settings.SESSION_TTL or 3600  # 1 hour default
        self.refresh_threshold = 300  # 5 minutes before expiration

    def _get_session_key(self, session_id: str) -> str:
        """
        Get Redis key for session
        """
        return f"{self.session_prefix}{session_id}"

    def _get_user_sessions_key(self, user_id: int) -> str:
        """
        Get Redis key for user's sessions list
        """
        return f"{self.user_sessions_prefix}{user_id}"

    async def create_session(
        self,
        user_id: int,
        user_data: Dict[str, Any],
        client_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new session for user
        """
        session_id = secrets.token_urlsafe(32)
        session_key = self._get_session_key(session_id)

        # Session data
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=self.session_ttl)).isoformat(),
            "client_info": client_info or {},
            "is_active": True,
            "refresh_count": 0,
        }

        # Store session data
        await cache_service.set(session_key, session_data, ttl=self.session_ttl)

        # Add to user's sessions list
        user_sessions_key = self._get_user_sessions_key(user_id)
        await cache_service.lpush(user_sessions_key, session_id)
        await cache_service.expire(user_sessions_key, self.session_ttl * 2)  # Keep list longer

        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        """
        session_key = self._get_session_key(session_id)
        session_data = await cache_service.get(session_key)

        if not session_data:
            return None

        # Check if session is expired
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.delete_session(session_id)
            return None

        # Update last accessed time
        session_data["last_accessed"] = datetime.utcnow().isoformat()
        await cache_service.set(session_key, session_data, ttl=self.session_ttl)

        return session_data

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False

        session_data.update(updates)
        session_data["last_accessed"] = datetime.utcnow().isoformat()

        session_key = self._get_session_key(session_id)
        return await cache_service.set(session_key, session_data, ttl=self.session_ttl)

    async def refresh_session(self, session_id: str) -> bool:
        """
        Refresh session expiration
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False

        # Check if refresh is needed
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        time_to_expiry = (expires_at - datetime.utcnow()).total_seconds()

        if time_to_expiry > self.refresh_threshold:
            return True  # No need to refresh yet

        # Extend session
        new_expires_at = datetime.utcnow() + timedelta(seconds=self.session_ttl)
        session_data["expires_at"] = new_expires_at.isoformat()
        session_data["refresh_count"] = session_data.get("refresh_count", 0) + 1

        session_key = self._get_session_key(session_id)
        result = await cache_service.set(session_key, session_data, ttl=self.session_ttl)

        if result:
            logger.info(f"Refreshed session {session_id}")

        return result

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return True  # Already deleted

        # Remove from user's sessions list
        user_id = session_data["user_id"]
        user_sessions_key = self._get_user_sessions_key(user_id)
        await cache_service.lrem(user_sessions_key, 0, session_id)

        # Delete session data
        session_key = self._get_session_key(session_id)
        result = await cache_service.delete(session_key)

        logger.info(f"Deleted session {session_id} for user {user_id}")
        return result

    async def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all active sessions for user
        """
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids = await cache_service.lrange(user_sessions_key, 0, -1)

        sessions = []
        for session_id in session_ids:
            session_data = await self.get_session(session_id)
            if session_data:
                sessions.append(session_data)

        return sessions

    async def delete_user_sessions(self, user_id: str, exclude_session_id: Optional[str] = None) -> int:
        """
        Delete all sessions for user except specified one
        """
        sessions = await self.get_user_sessions(user_id)
        deleted_count = 0

        for session in sessions:
            if session["session_id"] != exclude_session_id:
                if await self.delete_session(session["session_id"]):
                    deleted_count += 1

        logger.info(f"Deleted {deleted_count} sessions for user {user_id}")
        return deleted_count

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        """
        # This is a simplified cleanup - in production, you might want to use
        # Redis keyspace notifications or a scheduled task
        try:
            pattern = f"{self.session_prefix}*"
            # Note: This requires Redis KEYS command which can be slow on large datasets
            # Consider using SCAN in production
            session_keys = await cache_service.lrange("all_sessions", 0, -1)

            deleted_count = 0
            for session_key in session_keys:
                session_data = await cache_service.get(session_key)
                if session_data:
                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    if datetime.utcnow() > expires_at:
                        session_id = session_key.replace(self.session_prefix, "")
                        await self.delete_session(session_id)
                        deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired sessions")

            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate session and return user data
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return None

        # Check if session is active
        if not session_data.get("is_active", True):
            await self.delete_session(session_id)
            return None

        # Refresh session if needed
        await self.refresh_session(session_id)

        return session_data

    async def get_session_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get session statistics
        """
        stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "expired_sessions": 0,
            "average_session_duration": 0,
        }

        if user_id:
            sessions = await self.get_user_sessions(user_id)
            stats["total_sessions"] = len(sessions)
            stats["active_sessions"] = len([s for s in sessions if s.get("is_active", True)])

            # Calculate average session duration
            durations = []
            for session in sessions:
                created_at = datetime.fromisoformat(session["created_at"])
                last_accessed = datetime.fromisoformat(session["last_accessed"])
                duration = (last_accessed - created_at).total_seconds()
                durations.append(duration)

            if durations:
                stats["average_session_duration"] = sum(durations) / len(durations)

        return stats

    async def update_client_info(self, session_id: str, client_info: Dict[str, Any]) -> bool:
        """
        Update client information for session
        """
        return await self.update_session(session_id, {"client_info": client_info})


# Global session service instance
session_service = SessionService()