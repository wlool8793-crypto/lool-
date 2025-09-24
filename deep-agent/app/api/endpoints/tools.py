"""
Tool management endpoints for the Deep Agent application.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.core.database import get_db
from app.models import User, ToolExecution
from app.schemas.tool import (
    ToolListResponse, ToolExecutionRequest, ToolExecutionResponse,
    ToolHistoryResponse, ToolCategoryResponse
)
from app.services.tool import ToolService
from app.api.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ToolListResponse])
async def get_available_tools(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available tools."""
    tool_service = ToolService(db)
    tools = tool_service.get_available_tools(category=category)
    return [ToolListResponse.from_orm(tool) for tool in tools]


@router.get("/categories", response_model=List[ToolCategoryResponse])
async def get_tool_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tool categories."""
    tool_service = ToolService(db)
    categories = tool_service.get_tool_categories()
    return [ToolCategoryResponse.from_orm(category) for category in categories]


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a tool with the given parameters."""
    tool_service = ToolService(db)

    # Verify conversation belongs to user
    from app.models import Conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Execute tool
    try:
        result = await tool_service.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            conversation_id=request.conversation_id,
            user_id=current_user.id
        )

        return ToolExecutionResponse(
            success=result["success"],
            result=result.get("result"),
            execution_time=result.get("execution_time", 0),
            tool_name=request.tool_name,
            error_message=result.get("error_message")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.get("/history/{conversation_id}", response_model=List[ToolHistoryResponse])
async def get_tool_execution_history(
    conversation_id: int,
    tool_name: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tool execution history for a conversation."""
    tool_service = ToolService(db)

    # Verify conversation belongs to user
    from app.models import Conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    history = tool_service.get_execution_history(
        conversation_id=conversation_id,
        tool_name=tool_name,
        limit=limit
    )
    return [ToolHistoryResponse.from_orm(execution) for execution in history]


@router.get("/schema/{tool_name}")
async def get_tool_schema(
    tool_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the schema/parameters for a specific tool."""
    tool_service = ToolService(db)

    schema = tool_service.get_tool_schema(tool_name)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )

    return {
        "tool_name": tool_name,
        "schema": schema,
        "description": schema.get("description", ""),
        "parameters": schema.get("parameters", {})
    }


@router.post("/validate/{tool_name}")
async def validate_tool_parameters(
    tool_name: str,
    parameters: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate tool parameters before execution."""
    tool_service = ToolService(db)

    validation_result = tool_service.validate_tool_parameters(
        tool_name=tool_name,
        parameters=parameters
    )

    return {
        "tool_name": tool_name,
        "is_valid": validation_result["is_valid"],
        "errors": validation_result.get("errors", []),
        "warnings": validation_result.get("warnings", [])
    }


@router.get("/stats/{conversation_id}")
async def get_tool_usage_stats(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tool usage statistics for a conversation."""
    tool_service = ToolService(db)

    # Verify conversation belongs to user
    from app.models import Conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    stats = tool_service.get_usage_stats(conversation_id)
    return {
        "conversation_id": conversation_id,
        "total_executions": stats["total_executions"],
        "successful_executions": stats["successful_executions"],
        "failed_executions": stats["failed_executions"],
        "average_execution_time": stats["average_execution_time"],
        "most_used_tools": stats["most_used_tools"],
        "execution_by_category": stats["execution_by_category"]
    }


@router.delete("/history/{conversation_id}")
async def clear_tool_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear tool execution history for a conversation."""
    tool_service = ToolService(db)

    # Verify conversation belongs to user
    from app.models import Conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    tool_service.clear_history(conversation_id)
    return {"message": "Tool history cleared successfully"}


@router.post("/batch-execute")
async def execute_tools_batch(
    requests: List[ToolExecutionRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute multiple tools in batch."""
    tool_service = ToolService(db)

    # Verify all conversations belong to user
    from app.models import Conversation
    conversation_ids = [req.conversation_id for req in requests]
    conversations = db.query(Conversation).filter(
        Conversation.id.in_(conversation_ids),
        Conversation.user_id == current_user.id
    ).all()

    if len(conversations) != len(set(conversation_ids)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to one or more conversations"
        )

    # Execute tools in batch
    results = []
    for request in requests:
        try:
            result = await tool_service.execute_tool(
                tool_name=request.tool_name,
                parameters=request.parameters,
                conversation_id=request.conversation_id,
                user_id=current_user.id
            )
            results.append({
                "request": request.dict(),
                "result": result,
                "success": True
            })
        except Exception as e:
            results.append({
                "request": request.dict(),
                "error": str(e),
                "success": False
            })

    return {
        "batch_id": f"batch_{current_user.id}_{len(results)}",
        "total_requests": len(requests),
        "successful_executions": sum(1 for r in results if r["success"]),
        "failed_executions": sum(1 for r in results if not r["success"]),
        "results": results
    }