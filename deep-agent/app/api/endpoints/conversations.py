"""
Conversation management endpoints for the Deep Agent application.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.models import User, Conversation, Message
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse, ConversationListResponse
)
from app.services.conversation import ConversationService
from app.api.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ConversationListResponse])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user."""
    conversation_service = ConversationService(db)
    conversations = conversation_service.get_user_conversations(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return [ConversationListResponse.from_orm(conv) for conv in conversations]


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    conversation_service = ConversationService(db)

    # Generate unique session ID if not provided
    if not conversation_data.session_id:
        conversation_data.session_id = str(uuid.uuid4())

    conversation = conversation_service.create(
        user_id=current_user.id,
        **conversation_data.dict()
    )
    return ConversationResponse.from_orm(conversation)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation by ID."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ConversationResponse.from_orm(conversation)


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a conversation."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    updated_conversation = conversation_service.update(
        conversation_id=conversation_id,
        **conversation_data.dict(exclude_unset=True)
    )
    return ConversationResponse.from_orm(updated_conversation)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    conversation_service.delete(conversation_id)
    return {"message": "Conversation deleted successfully"}


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a conversation."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    messages = conversation_service.get_messages(
        conversation_id=conversation_id,
        skip=skip,
        limit=limit
    )
    return [MessageResponse.from_orm(msg) for msg in messages]


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new message in a conversation."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_by_id(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    message = conversation_service.create_message(
        conversation_id=conversation_id,
        **message_data.dict()
    )
    return MessageResponse.from_orm(message)


@router.get("/session/{session_id}", response_model=ConversationResponse)
async def get_conversation_by_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a conversation by session ID."""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_by_session_id(session_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ConversationResponse.from_orm(conversation)