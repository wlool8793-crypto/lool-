"""
WebSocket connection manager for real-time communication.
"""
import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket
from app.core.redis import redis_manager


class WebSocketManager:
    """Manages WebSocket connections and broadcasting."""

    def __init__(self):
        # Store active connections: {conversation_id: Set[WebSocket]}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store user connections: {user_id: Set[WebSocket]}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        # Store connection metadata: {websocket: {"user_id": int, "conversation_id": int}}
        self.connection_metadata: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, conversation_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()

        # Initialize sets if they don't exist
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        self.active_connections[conversation_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, conversation_id: int = None):
        """Remove a WebSocket connection."""
        # Remove from conversation connections
        if conversation_id and conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

        # Remove from user connections
        if websocket in self.connection_metadata:
            user_id = self.connection_metadata[websocket].get("user_id")
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

    def set_connection_metadata(self, websocket: WebSocket, metadata: Dict):
        """Set metadata for a WebSocket connection."""
        self.connection_metadata[websocket] = metadata

        # Add to user connections if user_id is provided
        user_id = metadata.get("user_id")
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            # Connection might be closed, remove it
            await self.disconnect(websocket)

    async def broadcast_to_conversation(self, conversation_id: int, message: str):
        """Broadcast a message to all connections in a conversation."""
        if conversation_id in self.active_connections:
            # Create a copy of the set to avoid modification during iteration
            connections = self.active_connections[conversation_id].copy()
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    # Remove failed connection
                    await self.disconnect(connection, conversation_id)

    async def broadcast_to_user(self, user_id: int, message: str):
        """Broadcast a message to all connections for a user."""
        if user_id in self.user_connections:
            # Create a copy of the set to avoid modification during iteration
            connections = self.user_connections[user_id].copy()
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    # Remove failed connection
                    await self.disconnect(connection)

    async def broadcast_to_all(self, message: str):
        """Broadcast a message to all active connections."""
        # Create a list of all connections to avoid modification issues
        all_connections = []
        for conversation_connections in self.active_connections.values():
            all_connections.extend(conversation_connections)

        for connection in all_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                # Remove failed connection
                await self.disconnect(connection)

    async def send_agent_update(self, conversation_id: int, update_data: Dict):
        """Send agent status update to conversation."""
        message = json.dumps({
            "type": "agent_update",
            "conversation_id": conversation_id,
            "data": update_data,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_conversation(conversation_id, message)

    async def send_tool_execution_update(self, conversation_id: int, tool_data: Dict):
        """Send tool execution update to conversation."""
        message = json.dumps({
            "type": "tool_update",
            "conversation_id": conversation_id,
            "data": tool_data,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_conversation(conversation_id, message)

    async def send_message_update(self, conversation_id: int, message_data: Dict):
        """Send message update to conversation."""
        message = json.dumps({
            "type": "message_update",
            "conversation_id": conversation_id,
            "data": message_data,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_conversation(conversation_id, message)

    async def send_error_update(self, conversation_id: int, error_data: Dict):
        """Send error update to conversation."""
        message = json.dumps({
            "type": "error_update",
            "conversation_id": conversation_id,
            "data": error_data,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_conversation(conversation_id, message)

    async def send_typing_indicator(self, conversation_id: int, user_id: int, is_typing: bool):
        """Send typing indicator to conversation."""
        message = json.dumps({
            "type": "typing_indicator",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_conversation(conversation_id, message)

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())

    def get_conversation_connection_count(self, conversation_id: int) -> int:
        """Get number of active connections for a conversation."""
        return len(self.active_connections.get(conversation_id, set()))

    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user."""
        return len(self.user_connections.get(user_id, set()))

    def get_active_conversations(self) -> List[int]:
        """Get list of conversation IDs with active connections."""
        return list(self.active_connections.keys())

    def get_active_users(self) -> List[int]:
        """Get list of user IDs with active connections."""
        return list(self.user_connections.keys())

    async def ping_all_connections(self):
        """Send ping to all active connections to check connectivity."""
        message = json.dumps({
            "type": "ping",
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_all(message)

    async def close_all_connections(self):
        """Close all active WebSocket connections."""
        all_connections = []
        for conversation_connections in self.active_connections.values():
            all_connections.extend(conversation_connections)

        for connection in all_connections:
            try:
                await connection.close()
            except Exception:
                pass  # Connection might already be closed

        # Clear all connection data
        self.active_connections.clear()
        self.user_connections.clear()
        self.connection_metadata.clear()

    async def send_system_notification(self, message: str, notification_type: str = "info"):
        """Send system notification to all users."""
        notification = json.dumps({
            "type": "system_notification",
            "notification_type": notification_type,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        })
        await self.broadcast_to_all(notification)