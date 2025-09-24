"""
LangGraph agent graph builder and orchestration.
"""
from typing import Dict, List, Any, Optional, Literal
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolExecutor  # Deprecated in newer versions
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json

from app.core.config import settings
from app.core.redis import redis_manager


class AgentState(BaseModel):
    """State schema for the agent graph."""

    # Input/Output
    user_input: str = Field(description="User's input message")
    final_response: Optional[str] = Field(default=None, description="Final response to user")

    # Conversation tracking
    conversation_id: str = Field(description="Unique conversation identifier")
    message_id: str = Field(description="Current message identifier")
    session_id: str = Field(description="User session identifier")

    # Task breakdown and planning
    task_breakdown: List[Dict[str, Any]] = Field(default_factory=list, description="Broken down tasks")
    current_task_index: int = Field(default=0, description="Current task being processed")

    # Tool selection and execution
    selected_tools: List[str] = Field(default_factory=list, description="Tools selected for execution")
    tool_results: Dict[str, Any] = Field(default_factory=dict, description="Results from tool executions")
    tool_errors: Dict[str, str] = Field(default_factory=dict, description="Errors from tool executions")

    # Context and memory
    context_memory: Dict[str, Any] = Field(default_factory=dict, description="Conversation context")
    entity_memory: Dict[str, Any] = Field(default_factory=dict, description="Entity tracking")
    summary_memory: Optional[str] = Field(default=None, description="Conversation summary")

    # Execution state
    current_node: str = Field(default="input_processing", description="Current graph node")
    status: str = Field(default="pending", description="Execution status")
    error_state: Optional[Dict[str, Any]] = Field(default=None, description="Error information")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    def update_timestamp(self):
        """Update the timestamp."""
        self.updated_at = datetime.now()

    def add_tool_result(self, tool_name: str, result: Any):
        """Add a tool execution result."""
        self.tool_results[tool_name] = result
        self.update_timestamp()

    def add_tool_error(self, tool_name: str, error: str):
        """Add a tool execution error."""
        self.tool_errors[tool_name] = error
        self.update_timestamp()

    def get_context_summary(self) -> str:
        """Get a summary of current context."""
        if self.summary_memory:
            return self.summary_memory

        # Create a basic summary from recent messages
        context_parts = []
        if self.task_breakdown:
            context_parts.append(f"Tasks: {len(self.task_breakdown)} items")
        if self.selected_tools:
            context_parts.append(f"Tools used: {', '.join(self.selected_tools)}")
        if self.tool_results:
            context_parts.append(f"Completed tools: {len(self.tool_results)}")

        return " | ".join(context_parts) if context_parts else "No context yet"


class AgentGraphBuilder:
    """Builder for creating the agent execution graph."""

    def __init__(self):
        self.graph = None
        self.tool_executor = None
        self._build_graph()

    def _build_graph(self):
        """Build the agent execution graph."""
        # Create the graph
        self.graph = StateGraph(AgentState)

        # Add nodes
        self.graph.add_node("input_processing", self._input_processing_node)
        self.graph.add_node("task_planning", self._task_planning_node)
        self.graph.add_node("tool_selection", self._tool_selection_node)
        self.graph.add_node("execution", self._execution_node)
        self.graph.add_node("memory_management", self._memory_management_node)
        self.graph.add_node("output_synthesis", self._output_synthesis_node)
        self.graph.add_node("error_handling", self._error_handling_node)

        # Define edges
        self.graph.add_edge("input_processing", "task_planning")
        self.graph.add_edge("task_planning", "tool_selection")
        self.graph.add_edge("tool_selection", "execution")
        self.graph.add_edge("execution", "memory_management")
        self.graph.add_edge("memory_management", "output_synthesis")
        self.graph.add_edge("output_synthesis", END)

        # Error handling edges
        self.graph.add_conditional_edges(
            "input_processing",
            self._check_input_error,
            {
                "error": "error_handling",
                "continue": "task_planning"
            }
        )

        self.graph.add_conditional_edges(
            "execution",
            self._check_execution_error,
            {
                "error": "error_handling",
                "continue": "memory_management"
            }
        )

        self.graph.add_conditional_edges(
            "error_handling",
            self._handle_error_recovery,
            {
                "retry": "input_processing",
                "fail": END
            }
        )

        # Set entry point
        self.graph.set_entry_point("input_processing")

    def _input_processing_node(self, state: AgentState) -> Dict[str, Any]:
        """Process and validate user input."""
        try:
            # Update current node
            state.current_node = "input_processing"
            state.status = "processing"

            # Basic input validation
            if not state.user_input or not state.user_input.strip():
                raise ValueError("Empty input")

            # Sanitize input
            sanitized_input = state.user_input.strip()
            state.user_input = sanitized_input

            # Extract basic metadata
            input_length = len(sanitized_input)
            state.metadata["input_length"] = input_length
            state.metadata["input_type"] = self._detect_input_type(sanitized_input)

            # Update status
            state.status = "completed"

            return {
                "user_input": state.user_input,
                "metadata": state.metadata,
                "status": state.status,
                "current_node": state.current_node
            }

        except Exception as e:
            state.error_state = {
                "node": "input_processing",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            state.status = "error"

            return {
                "error_state": state.error_state,
                "status": state.status,
                "current_node": state.current_node
            }

    def _task_planning_node(self, state: AgentState) -> Dict[str, Any]:
        """Break down complex tasks into subtasks."""
        try:
            state.current_node = "task_planning"
            state.status = "processing"

            # Simple task planning (can be enhanced with LLM)
            tasks = self._plan_tasks(state.user_input)
            state.task_breakdown = tasks

            # Update metadata
            state.metadata["task_count"] = len(tasks)
            state.metadata["planning_completed"] = True

            state.status = "completed"

            return {
                "task_breakdown": state.task_breakdown,
                "metadata": state.metadata,
                "status": state.status,
                "current_node": state.current_node
            }

        except Exception as e:
            state.error_state = {
                "node": "task_planning",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            state.status = "error"

            return {
                "error_state": state.error_state,
                "status": state.status,
                "current_node": state.current_node
            }

    def _tool_selection_node(self, state: AgentState) -> Dict[str, Any]:
        """Select appropriate tools for each task."""
        try:
            state.current_node = "tool_selection"
            state.status = "processing"

            # Select tools based on tasks
            tools = self._select_tools_for_tasks(state.task_breakdown)
            state.selected_tools = tools

            # Update metadata
            state.metadata["selected_tools"] = tools
            state.metadata["tool_selection_completed"] = True

            state.status = "completed"

            return {
                "selected_tools": state.selected_tools,
                "metadata": state.metadata,
                "status": state.status,
                "current_node": state.current_node
            }

        except Exception as e:
            state.error_state = {
                "node": "tool_selection",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            state.status = "error"

            return {
                "error_state": state.error_state,
                "status": state.status,
                "current_node": state.current_node
            }

    def _execution_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute selected tools."""
        try:
            state.current_node = "execution"
            state.status = "processing"

            # Execute tools (placeholder for actual tool execution)
            results = self._execute_tools(state.selected_tools, state)

            # Update results
            for tool_name, result in results.items():
                if isinstance(result, Exception):
                    state.add_tool_error(tool_name, str(result))
                else:
                    state.add_tool_result(tool_name, result)

            # Update metadata
            state.metadata["execution_completed"] = True
            state.metadata["successful_tools"] = len(state.tool_results)
            state.metadata["failed_tools"] = len(state.tool_errors)

            state.status = "completed"

            return {
                "tool_results": state.tool_results,
                "tool_errors": state.tool_errors,
                "metadata": state.metadata,
                "status": state.status,
                "current_node": state.current_node
            }

        except Exception as e:
            state.error_state = {
                "node": "execution",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            state.status = "error"

            return {
                "error_state": state.error_state,
                "status": state.status,
                "current_node": state.current_node
            }

    def _memory_management_node(self, state: AgentState) -> Dict[str, Any]:
        """Manage conversation memory and context."""
        try:
            state.current_node = "memory_management"
            state.status = "processing"

            # Update context memory
            self._update_context_memory(state)

            # Update entity memory
            self._update_entity_memory(state)

            # Generate summary if needed
            if len(state.task_breakdown) > 3:
                state.summary_memory = self._generate_summary(state)

            # Store in Redis for persistence
            self._store_state_in_redis(state)

            state.status = "completed"

            return {
                "context_memory": state.context_memory,
                "entity_memory": state.entity_memory,
                "summary_memory": state.summary_memory,
                "status": state.status,
                "current_node": state.current_node
            }

        except Exception as e:
            state.error_state = {
                "node": "memory_management",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            state.status = "error"

            return {
                "error_state": state.error_state,
                "status": state.status,
                "current_node": state.current_node
            }

    def _output_synthesis_node(self, state: AgentState) -> Dict[str, Any]:
        """Synthesize final response."""
        try:
            state.current_node = "output_synthesis"
            state.status = "processing"

            # Generate final response
            response = self._generate_response(state)
            state.final_response = response

            # Update metadata
            state.metadata["response_generated"] = True
            state.metadata["response_length"] = len(response)

            state.status = "completed"

            return {
                "final_response": state.final_response,
                "metadata": state.metadata,
                "status": state.status,
                "current_node": state.current_node
            }

        except Exception as e:
            state.error_state = {
                "node": "output_synthesis",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            state.status = "error"

            return {
                "error_state": state.error_state,
                "status": state.status,
                "current_node": state.current_node
            }

    def _error_handling_node(self, state: AgentState) -> Dict[str, Any]:
        """Handle errors and decide on recovery strategy."""
        state.current_node = "error_handling"
        state.status = "error"

        error_info = state.error_state or {}
        error_node = error_info.get("node", "unknown")
        error_message = error_info.get("error", "Unknown error")

        # Log the error
        print(f"Error in {error_node}: {error_message}")

        # Simple retry logic (can be enhanced)
        if error_node in ["input_processing", "tool_selection"]:
            # Retry for these nodes
            return {"retry_decision": "retry"}
        else:
            # Fail for other nodes
            return {"retry_decision": "fail"}

    # Conditional edge functions
    def _check_input_error(self, state: AgentState) -> Literal["error", "continue"]:
        return "error" if state.error_state else "continue"

    def _check_execution_error(self, state: AgentState) -> Literal["error", "continue"]:
        return "error" if state.error_state else "continue"

    def _handle_error_recovery(self, state: AgentState) -> Literal["retry", "fail"]:
        error_info = state.error_state or {}
        error_node = error_info.get("node", "unknown")

        if error_node in ["input_processing", "tool_selection"]:
            return "retry"
        return "fail"

    # Helper methods
    def _detect_input_type(self, input_text: str) -> str:
        """Detect the type of input."""
        input_lower = input_text.lower()

        if any(word in input_lower for word in ["search", "find", "look up", "google"]):
            return "search"
        elif any(word in input_lower for word in ["analyze", "summarize", "explain"]):
            return "analysis"
        elif any(word in input_lower for word in ["create", "generate", "make", "build"]):
            return "creation"
        elif any(word in input_lower for word in ["help", "how to", "what is"]):
            return "question"
        else:
            return "general"

    def _plan_tasks(self, input_text: str) -> List[Dict[str, Any]]:
        """Plan tasks based on input (simplified version)."""
        tasks = []
        input_type = self._detect_input_type(input_text)

        # Basic task planning
        if input_type == "search":
            tasks.append({
                "id": "search_query",
                "type": "search",
                "description": "Search for relevant information",
                "priority": "high"
            })
            tasks.append({
                "id": "process_results",
                "type": "processing",
                "description": "Process and summarize search results",
                "priority": "medium"
            })
        elif input_type == "analysis":
            tasks.append({
                "id": "gather_data",
                "type": "data_collection",
                "description": "Gather data for analysis",
                "priority": "high"
            })
            tasks.append({
                "id": "analyze_data",
                "type": "analysis",
                "description": "Perform data analysis",
                "priority": "high"
            })
            tasks.append({
                "id": "generate_summary",
                "type": "synthesis",
                "description": "Generate analysis summary",
                "priority": "medium"
            })
        else:
            # Default task structure
            tasks.append({
                "id": "process_request",
                "type": "general",
                "description": "Process user request",
                "priority": "high"
            })
            tasks.append({
                "id": "generate_response",
                "type": "synthesis",
                "description": "Generate appropriate response",
                "priority": "medium"
            })

        return tasks

    def _select_tools_for_tasks(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Select tools based on tasks."""
        tools = []

        for task in tasks:
            task_type = task.get("type", "general")

            if task_type == "search":
                tools.extend(["web_search", "document_retrieval"])
            elif task_type == "analysis":
                tools.extend(["data_analyzer", "document_processor"])
            elif task_type == "creation":
                tools.extend(["code_generator", "content_creator"])
            elif task_type == "data_collection":
                tools.extend(["web_scraper", "api_connector"])

            # Add common tools
            tools.extend(["memory_manager", "error_handler"])

        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for tool in tools:
            if tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)

        return unique_tools

    def _execute_tools(self, tools: List[str], state: AgentState) -> Dict[str, Any]:
        """Execute tools (placeholder implementation)."""
        results = {}

        for tool in tools:
            try:
                # Placeholder for actual tool execution
                if tool == "web_search":
                    results[tool] = {"status": "completed", "results": ["Search results placeholder"]}
                elif tool == "document_processor":
                    results[tool] = {"status": "completed", "processed": True}
                elif tool == "memory_manager":
                    results[tool] = {"status": "completed", "memory_updated": True}
                else:
                    results[tool] = {"status": "completed", "message": f"Tool {tool} executed"}

            except Exception as e:
                results[tool] = e

        return results

    def _update_context_memory(self, state: AgentState):
        """Update context memory."""
        # Simple context management
        state.context_memory.update({
            "last_input": state.user_input,
            "task_count": len(state.task_breakdown),
            "tools_used": state.selected_tools,
            "timestamp": datetime.now().isoformat()
        })

    def _update_entity_memory(self, state: AgentState):
        """Update entity memory (simplified)."""
        # Extract basic entities (can be enhanced with NLP)
        entities = {}

        # Extract potential entities from input
        words = state.user_input.split()
        for word in words:
            if word.istitle() and len(word) > 2:
                entities[word.lower()] = entities.get(word.lower(), 0) + 1

        state.entity_memory.update(entities)

    def _generate_summary(self, state: AgentState) -> str:
        """Generate conversation summary."""
        task_summary = f"Processed {len(state.task_breakdown)} tasks"
        tool_summary = f"Used {len(state.selected_tools)} tools"
        result_summary = f"Completed {len(state.tool_results)} successfully"

        return f"{task_summary}, {tool_summary}, {result_summary}"

    def _store_state_in_redis(self, state: AgentState):
        """Store state in Redis for persistence."""
        try:
            redis_key = f"agent_state:{state.conversation_id}"
            redis_manager.set(redis_key, state.dict(), ex=3600)  # 1 hour expiry
        except Exception as e:
            print(f"Failed to store state in Redis: {e}")

    def _generate_response(self, state: AgentState) -> str:
        """Generate final response."""
        if state.final_response:
            return state.final_response

        # Generate response based on results
        if state.tool_results:
            response_parts = []
            response_parts.append("I've processed your request using several tools:")

            for tool, result in state.tool_results.items():
                response_parts.append(f"- {tool}: {result.get('message', 'Completed successfully')}")

            if state.summary_memory:
                response_parts.append(f"\nSummary: {state.summary_memory}")

            return "\n".join(response_parts)

        else:
            return "I understand your request. Let me help you with that."

    def compile(self):
        """Compile the graph for execution."""
        if self.graph is None:
            raise ValueError("Graph not built")

        return self.graph.compile()


# Global graph instance
agent_graph = AgentGraphBuilder().compile()