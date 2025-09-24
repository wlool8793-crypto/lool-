"""
Conversation service for the Deep Agent application.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Conversation, Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate


class ConversationService:
    """Service for conversation management."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        return self.db.query(Conversation).filter(Conversation.session_id == session_id).first()

    def get_user_conversations(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user with pagination."""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def create(self, user_id: int, **kwargs) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=user_id, **kwargs)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def update(self, conversation_id: int, **kwargs) -> Optional[Conversation]:
        """Update conversation information."""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return None

        for key, value in kwargs.items():
            setattr(conversation, key, value)

        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete(self, conversation_id: int) -> bool:
        """Delete a conversation."""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True

    def create_message(self, conversation_id: int, **kwargs) -> Message:
        """Create a new message in a conversation."""
        message = Message(conversation_id=conversation_id, **kwargs)
        self.db.add(message)

        # Update conversation updated_at timestamp
        conversation = self.get_by_id(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get messages for a conversation with pagination."""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

    def get_message_by_id(self, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        return self.db.query(Message).filter(Message.id == message_id).first()

    def update_message(self, message_id: int, **kwargs) -> Optional[Message]:
        """Update message content."""
        message = self.get_message_by_id(message_id)
        if not message:
            return None

        for key, value in kwargs.items():
            setattr(message, key, value)

        self.db.commit()
        self.db.refresh(message)
        return message

    def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        message = self.get_message_by_id(message_id)
        if not message:
            return False

        self.db.delete(message)
        self.db.commit()
        return True

    def get_conversation_count(self, user_id: int) -> int:
        """Get conversation count for a user."""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).count()

    def get_message_count(self, conversation_id: int) -> int:
        """Get message count for a conversation."""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()

    def get_last_message(self, conversation_id: int) -> Optional[Message]:
        """Get the last message in a conversation."""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).first()

    def search_conversations(self, user_id: int, query: str, skip: int = 0, limit: int = 50) -> List[Conversation]:
        """Search conversations by title or message content."""
        search_pattern = f"%{query}%"
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            (Conversation.title.ilike(search_pattern)) |
            (Conversation.messages.any(Message.content.ilike(search_pattern)))
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def get_recent_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Get recent conversations for a user."""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).limit(limit).all()

    def archive_conversation(self, conversation_id: int) -> bool:
        """Archive a conversation (mark as inactive)."""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return False

        conversation.metadata = conversation.metadata or {}
        conversation.metadata["archived"] = True
        conversation.metadata["archived_at"] = datetime.utcnow().isoformat()
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def unarchive_conversation(self, conversation_id: int) -> bool:
        """Unarchive a conversation."""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return False

        conversation.metadata = conversation.metadata or {}
        conversation.metadata["archived"] = False
        conversation.metadata["unarchived_at"] = datetime.utcnow().isoformat()
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        return True