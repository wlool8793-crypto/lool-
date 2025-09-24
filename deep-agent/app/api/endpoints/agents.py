"""
Agent management endpoints for the Deep Agent application.
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import asyncio

from app.core.database import get_db
from app.models import User, Conversation, AgentState
from app.schemas.agent import (
    AgentCreate, AgentResponse, AgentExecuteRequest, AgentExecuteResponse,
    AgentStatusResponse, AgentListResponse
)
from app.services.agent import AgentService
from app.api.endpoints.auth import get_current_user
from app.websocket.manager import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()


@router.get("/", response_model=List[AgentListResponse])
async def get_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available agent types and configurations."""
    agent_service = AgentService(db)
    agents = agent_service.get_available_agents()
    return [AgentListResponse.from_orm(agent) for agent in agents]


@router.post("/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    request: AgentExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute an agent with the given request."""
    agent_service = AgentService(db)

    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Execute agent
    try:
        result = await agent_service.execute_agent(
            conversation_id=request.conversation_id,
            message=request.message,
            agent_type=request.agent_type,
            tools=request.tools,
            context=request.context
        )

        return AgentExecuteResponse(
            success=True,
            response=result["response"],
            execution_time=result["execution_time"],
            tools_used=result.get("tools_used", []),
            tokens_used=result.get("tokens_used", 0),
            agent_state=result.get("agent_state")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/status/{conversation_id}", response_model=AgentStatusResponse)
async def get_agent_status(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current status of an agent execution."""
    agent_service = AgentService(db)

    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get agent state
    agent_state = agent_service.get_agent_state(conversation_id)
    return AgentStatusResponse(
        conversation_id=conversation_id,
        status=agent_state.status if agent_state else "idle",
        current_node=agent_state.current_node if agent_state else None,
        state_data=agent_state.state_data if agent_state else None,
        error_message=agent_state.error_message if agent_state else None,
        updated_at=agent_state.updated_at if agent_state else None
    )


@router.get("/history/{conversation_id}")
async def get_agent_execution_history(
    conversation_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get execution history for a conversation."""
    agent_service = AgentService(db)

    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    history = agent_service.get_execution_history(conversation_id, limit)
    return {
        "conversation_id": conversation_id,
        "executions": history,
        "total_count": len(history)
    }


@router.delete("/state/{conversation_id}")
async def clear_agent_state(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear agent state for a conversation."""
    agent_service = AgentService(db)

    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    agent_service.clear_agent_state(conversation_id)
    return {"message": "Agent state cleared successfully"}


@router.post("/stop/{conversation_id}")
async def stop_agent_execution(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop agent execution for a conversation."""
    agent_service = AgentService(db)

    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    agent_service.stop_execution(conversation_id)
    return {"message": "Agent execution stopped"}


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str
):
    """WebSocket endpoint for real-time agent communication."""
    # Authenticate with token
    try:
        # This is a simplified auth - in production, you'd want proper JWT validation
        await websocket_manager.connect(websocket, conversation_id)
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "conversation_id": conversation_id
        }))

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Handle different message types
                if message_data.get("type") == "message":
                    # Process message through agent
                    response = {
                        "type": "agent_response",
                        "content": f"Processing: {message_data.get('content', '')}",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    await websocket.send_text(json.dumps(response))

                elif message_data.get("type") == "status_request":
                    # Send current agent status
                    status_response = {
                        "type": "status",
                        "status": "active",
                        "conversation_id": conversation_id
                    }
                    await websocket.send_text(json.dumps(status_response))

                elif message_data.get("type") == "ping":
                    # Respond to ping
                    await websocket.send_text(json.dumps({"type": "pong"}))

        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, conversation_id)
            # Notify other clients about disconnection
            await websocket_manager.broadcast_to_conversation(
                conversation_id,
                json.dumps({
                    "type": "user_disconnected",
                    "conversation_id": conversation_id
                })
            )

    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
        websocket_manager.disconnect(websocket, conversation_id)