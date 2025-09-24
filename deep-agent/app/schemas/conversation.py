"""
Conversation schemas for the Deep Agent application.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    session_id: Optional[str] = Field(None, description="Unique session identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ConversationCreate(ConversationBase):
    """Conversation creation schema."""
    pass


class ConversationUpdate(BaseModel):
    """Conversation update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Conversation title")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ConversationResponse(ConversationBase):
    """Conversation response schema."""
    id: int = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    message_count: Optional[int] = Field(0, description="Number of messages")
    last_message: Optional[str] = Field(None, description="Last message content")

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Simplified conversation response for listing."""
    id: int = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title")
    session_id: str = Field(..., description="Session ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    message_count: int = Field(0, description="Number of messages")
    last_message: Optional[str] = Field(None, description="Last message content")

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., min_length=1, description="Message content")
    message_type: str = Field(default="text", description="Message type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v

    @validator('message_type')
    def validate_message_type(cls, v):
        allowed_types = ['text', 'file', 'system', 'tool_result', 'error']
        if v not in allowed_types:
            raise ValueError(f'Message type must be one of: {allowed_types}')
        return v


class MessageCreate(MessageBase):
    """Message creation schema."""
    conversation_id: int = Field(..., description="Conversation ID")


class MessageResponse(MessageBase):
    """Message response schema."""
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="Creation time")

    class Config:
        from_attributes = True


class ConversationWithMessagesResponse(ConversationResponse):
    """Conversation with messages response schema."""
    messages: List[MessageResponse] = Field(default_factory=list, description="Messages in conversation")

    class Config:
        from_attributes = True


class ConversationSearchRequest(BaseModel):
    """Conversation search request schema."""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class ConversationSearchResponse(BaseModel):
    """Conversation search response schema."""
    conversations: List[ConversationListResponse] = Field(default_factory=list, description="Search results")
    total_count: int = Field(0, description="Total results count")
    query: str = Field(..., description="Search query used")


class ConversationExportRequest(BaseModel):
    """Conversation export request schema."""
    conversation_ids: List[int] = Field(..., description="List of conversation IDs to export")
    format: str = Field(default="json", description="Export format (json, csv, txt)")
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    include_messages: bool = Field(default=True, description="Include messages in export")

    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['json', 'csv', 'txt']
        if v not in allowed_formats:
            raise ValueError(f'Format must be one of: {allowed_formats}')
        return v


class ConversationExportResponse(BaseModel):
    """Conversation export response schema."""
    export_data: str = Field(..., description="Exported data")
    format: str = Field(..., description="Export format")
    filename: str = Field(..., description="Suggested filename")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Export time")


class ConversationStatsResponse(BaseModel):
    """Conversation statistics response schema."""
    total_conversations: int = Field(0, description="Total conversations")
    total_messages: int = Field(0, description="Total messages")
    average_messages_per_conversation: float = Field(0.0, description="Average messages per conversation")
    conversations_created_today: int = Field(0, description="Conversations created today")
    conversations_created_this_week: int = Field(0, description="Conversations created this week")
    conversations_created_this_month: int = Field(0, description="Conversations created this month")
    most_active_hour: Optional[int] = Field(None, description="Most active hour (0-23)")
    conversation_growth: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation growth data")