"""
Agent schemas for the Deep Agent application.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: str = Field(..., min_length=1, description="Agent description")
    agent_type: str = Field(..., description="Agent type")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    is_active: bool = Field(default=True, description="Agent status")


class AgentCreate(AgentBase):
    """Agent creation schema."""
    pass


class AgentUpdate(BaseModel):
    """Agent update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Agent name")
    description: Optional[str] = Field(None, min_length=1, description="Agent description")
    capabilities: Optional[List[str]] = Field(None, description="Agent capabilities")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    is_active: Optional[bool] = Field(None, description="Agent status")


class AgentResponse(AgentBase):
    """Agent response schema."""
    id: int = Field(..., description="Agent ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Simplified agent response for listing."""
    id: int = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    agent_type: str = Field(..., description="Agent type")
    is_active: bool = Field(..., description="Agent status")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")

    class Config:
        from_attributes = True


class AgentExecuteRequest(BaseModel):
    """Agent execution request schema."""
    conversation_id: int = Field(..., description="Conversation ID")
    message: str = Field(..., min_length=1, description="Message to process")
    agent_type: str = Field(..., description="Agent type to use")
    tools: Optional[List[str]] = Field(None, description="Tools to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    max_iterations: Optional[int] = Field(default=10, ge=1, le=100, description="Maximum iterations")
    timeout: Optional[int] = Field(default=300, ge=1, le=3600, description="Timeout in seconds")


class AgentExecuteResponse(BaseModel):
    """Agent execution response schema."""
    success: bool = Field(..., description="Execution success status")
    response: str = Field(..., description="Agent response")
    execution_time: float = Field(..., description="Execution time in seconds")
    tools_used: List[str] = Field(default_factory=list, description="Tools used during execution")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    agent_state: Optional[Dict[str, Any]] = Field(None, description="Final agent state")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class AgentStatusResponse(BaseModel):
    """Agent status response schema."""
    conversation_id: int = Field(..., description="Conversation ID")
    status: str = Field(..., description="Agent status")
    current_node: Optional[str] = Field(None, description="Current node in execution graph")
    state_data: Optional[Dict[str, Any]] = Field(None, description="Current state data")
    error_message: Optional[str] = Field(None, description="Error message if any")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    execution_time: Optional[float] = Field(None, description="Current execution time in seconds")


class AgentNodeResponse(BaseModel):
    """Agent node response schema."""
    node_name: str = Field(..., description="Node name")
    node_type: str = Field(..., description="Node type")
    status: str = Field(..., description="Node status")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Node input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Node output data")
    execution_time: Optional[float] = Field(None, description="Node execution time")
    error_message: Optional[str] = Field(None, description="Error message if any")


class AgentExecutionHistory(BaseModel):
    """Agent execution history schema."""
    conversation_id: int = Field(..., description="Conversation ID")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Execution status")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    input_message: str = Field(..., description="Input message")
    response: Optional[str] = Field(None, description="Agent response")
    tools_used: List[str] = Field(default_factory=list, description="Tools used")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    error_message: Optional[str] = Field(None, description="Error message if any")
    nodes_executed: List[AgentNodeResponse] = Field(default_factory=list, description="Nodes executed")


class AgentStatsResponse(BaseModel):
    """Agent statistics response schema."""
    total_executions: int = Field(0, description="Total agent executions")
    successful_executions: int = Field(0, description="Successful executions")
    failed_executions: int = Field(0, description="Failed executions")
    average_execution_time: float = Field(0.0, description="Average execution time")
    most_used_agent_types: List[Dict[str, Any]] = Field(default_factory=list, description="Most used agent types")
    most_used_tools: List[Dict[str, Any]] = Field(default_factory=list, description="Most used tools")
    executions_by_day: List[Dict[str, Any]] = Field(default_factory=list, description="Executions by day")
    total_tokens_used: int = Field(0, description="Total tokens used")
    average_tokens_per_execution: float = Field(0.0, description="Average tokens per execution")


class AgentTemplate(BaseModel):
    """Agent template schema."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    agent_type: str = Field(..., description="Agent type")
    template_config: Dict[str, Any] = Field(..., description="Template configuration")
    prompt_template: Optional[str] = Field(None, description="Prompt template")
    tools: List[str] = Field(default_factory=list, description="Recommended tools")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    category: str = Field(..., description="Template category")
    is_builtin: bool = Field(default=True, description="Is built-in template")


class AgentTemplateResponse(AgentTemplate):
    """Agent template response schema."""
    id: int = Field(..., description="Template ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    usage_count: int = Field(0, description="Template usage count")

    class Config:
        from_attributes = True


class AgentConfiguration(BaseModel):
    """Agent configuration schema."""
    agent_type: str = Field(..., description="Agent type")
    config: Dict[str, Any] = Field(..., description="Configuration parameters")
    tools: List[str] = Field(default_factory=list, description="Enabled tools")
    max_iterations: int = Field(default=10, ge=1, le=100, description="Maximum iterations")
    timeout: int = Field(default=300, ge=1, le=3600, description="Timeout in seconds")
    memory_config: Optional[Dict[str, Any]] = Field(None, description="Memory configuration")
    logging_level: str = Field(default="INFO", description="Logging level")
    enable_tracing: bool = Field(default=False, description="Enable tracing")

    @validator('logging_level')
    def validate_logging_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in allowed_levels:
            raise ValueError(f'Logging level must be one of: {allowed_levels}')
        return v


class AgentBenchmark(BaseModel):
    """Agent benchmark schema."""
    agent_type: str = Field(..., description="Agent type")
    test_cases: int = Field(..., ge=1, description="Number of test cases")
    passed_tests: int = Field(..., ge=0, description="Number of passed tests")
    failed_tests: int = Field(..., ge=0, description="Number of failed tests")
    average_response_time: float = Field(..., ge=0, description="Average response time")
    average_tokens_used: float = Field(..., ge=0, description="Average tokens used")
    success_rate: float = Field(..., ge=0, le=1, description="Success rate")
    benchmark_date: datetime = Field(..., description="Benchmark date")
    test_details: List[Dict[str, Any]] = Field(default_factory=list, description="Test details")