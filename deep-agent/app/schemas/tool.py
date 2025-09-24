"""
Tool schemas for the Deep Agent application.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolBase(BaseModel):
    """Base tool schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Tool name")
    description: str = Field(..., min_length=1, description="Tool description")
    category: str = Field(..., description="Tool category")
    version: str = Field(..., description="Tool version")
    parameters_schema: Dict[str, Any] = Field(..., description="Parameters schema")
    is_active: bool = Field(default=True, description="Tool status")
    requires_auth: bool = Field(default=False, description="Requires authentication")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")


class ToolCreate(ToolBase):
    """Tool creation schema."""
    pass


class ToolUpdate(BaseModel):
    """Tool update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tool name")
    description: Optional[str] = Field(None, min_length=1, description="Tool description")
    category: Optional[str] = Field(None, description="Tool category")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="Parameters schema")
    is_active: Optional[bool] = Field(None, description="Tool status")
    requires_auth: Optional[bool] = Field(None, description="Requires authentication")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")


class ToolResponse(ToolBase):
    """Tool response schema."""
    id: int = Field(..., description="Tool ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    class Config:
        from_attributes = True


class ToolListResponse(BaseModel):
    """Simplified tool response for listing."""
    id: int = Field(..., description="Tool ID")
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: str = Field(..., description="Tool category")
    version: str = Field(..., description="Tool version")
    is_active: bool = Field(..., description="Tool status")
    requires_auth: bool = Field(..., description="Requires authentication")

    class Config:
        from_attributes = True


class ToolCategoryResponse(BaseModel):
    """Tool category response schema."""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    tool_count: int = Field(..., description="Number of tools in category")
    is_active: bool = Field(..., description="Category status")

    class Config:
        from_attributes = True


class ToolExecutionRequest(BaseModel):
    """Tool execution request schema."""
    tool_name: str = Field(..., description="Tool name")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    conversation_id: int = Field(..., description="Conversation ID")
    timeout: Optional[int] = Field(default=30, ge=1, le=300, description="Timeout in seconds")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ToolExecutionResponse(BaseModel):
    """Tool execution response schema."""
    success: bool = Field(..., description="Execution success status")
    result: Optional[Any] = Field(None, description="Execution result")
    execution_time: float = Field(..., description="Execution time in seconds")
    tool_name: str = Field(..., description="Tool name")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ToolHistoryResponse(BaseModel):
    """Tool execution history response schema."""
    id: int = Field(..., description="Execution ID")
    tool_name: str = Field(..., description="Tool name")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data")
    execution_time: Optional[int] = Field(None, description="Execution time in milliseconds")
    status: str = Field(..., description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if any")
    created_at: datetime = Field(..., description="Execution time")

    class Config:
        from_attributes = True


class ToolStatsResponse(BaseModel):
    """Tool statistics response schema."""
    tool_name: str = Field(..., description="Tool name")
    total_executions: int = Field(0, description="Total executions")
    successful_executions: int = Field(0, description="Successful executions")
    failed_executions: int = Field(0, description="Failed executions")
    average_execution_time: float = Field(0.0, description="Average execution time")
    last_used: Optional[datetime] = Field(None, description="Last used time")
    success_rate: float = Field(0.0, description="Success rate")
    usage_by_day: List[Dict[str, Any]] = Field(default_factory=list, description="Usage by day")


class ToolRegistry(BaseModel):
    """Tool registry schema."""
    tools: List[ToolResponse] = Field(default_factory=list, description="Available tools")
    categories: List[ToolCategoryResponse] = Field(default_factory=list, description="Tool categories")
    total_tools: int = Field(0, description="Total tools")
    active_tools: int = Field(0, description="Active tools")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


class ToolTemplate(BaseModel):
    """Tool template schema."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Tool category")
    template_code: str = Field(..., description="Template code")
    parameters_schema: Dict[str, Any] = Field(..., description="Parameters schema")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    is_builtin: bool = Field(default=True, description="Is built-in template")
    version: str = Field(..., description="Template version")


class ToolBenchmark(BaseModel):
    """Tool benchmark schema."""
    tool_name: str = Field(..., description="Tool name")
    test_cases: int = Field(..., ge=1, description="Number of test cases")
    passed_tests: int = Field(..., ge=0, description="Number of passed tests")
    failed_tests: int = Field(..., ge=0, description="Number of failed tests")
    average_execution_time: float = Field(..., ge=0, description="Average execution time")
    success_rate: float = Field(..., ge=0, le=1, description="Success rate")
    benchmark_date: datetime = Field(..., description="Benchmark date")
    test_details: List[Dict[str, Any]] = Field(default_factory=list, description="Test details")


class ToolValidationResult(BaseModel):
    """Tool validation result schema."""
    is_valid: bool = Field(..., description="Validation result")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    normalized_parameters: Optional[Dict[str, Any]] = Field(None, description="Normalized parameters")
    execution_time: Optional[float] = Field(None, description="Validation execution time")


class ToolHealthCheck(BaseModel):
    """Tool health check schema."""
    tool_name: str = Field(..., description="Tool name")
    is_healthy: bool = Field(..., description="Health status")
    response_time: float = Field(..., description="Response time")
    last_check: datetime = Field(..., description="Last check time")
    error_message: Optional[str] = Field(None, description="Error message if any")
    dependencies_status: Dict[str, bool] = Field(default_factory=dict, description="Dependencies status")


class ToolRateLimit(BaseModel):
    """Tool rate limit schema."""
    tool_name: str = Field(..., description="Tool name")
    limit: int = Field(..., description="Rate limit")
    current_usage: int = Field(0, description="Current usage")
    reset_time: datetime = Field(..., description="Reset time")
    is_limited: bool = Field(..., description="Is currently limited")


class ToolPermission(BaseModel):
    """Tool permission schema."""
    tool_name: str = Field(..., description="Tool name")
    user_id: int = Field(..., description="User ID")
    can_execute: bool = Field(..., description="Can execute tool")
    max_daily_executions: Optional[int] = Field(None, description="Max daily executions")
    custom_parameters: Optional[Dict[str, Any]] = Field(None, description="Custom parameters")
    granted_at: datetime = Field(..., description="Permission granted time")
    expires_at: Optional[datetime] = Field(None, description="Permission expiration time")