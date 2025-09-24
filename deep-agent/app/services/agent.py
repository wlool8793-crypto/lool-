"""
Agent service for the Deep Agent application.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
from app.models import AgentState, Conversation
from app.agents.graph_builder import AgentGraphBuilder


class AgentService:
    """Service for agent management and execution."""

    def __init__(self, db: Session):
        self.db = db
        self.graph_builder = AgentGraphBuilder()

    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agent types."""
        return [
            {
                "id": 1,
                "name": "General Assistant",
                "description": "General purpose AI assistant for various tasks",
                "agent_type": "general",
                "capabilities": ["text_processing", "web_search", "code_generation"],
                "config": {"model": "gpt-4", "temperature": 0.7},
                "is_active": True
            },
            {
                "id": 2,
                "name": "Research Agent",
                "description": "Specialized agent for research and analysis",
                "agent_type": "research",
                "capabilities": ["web_search", "document_analysis", "data_analysis"],
                "config": {"model": "gpt-4", "temperature": 0.3},
                "is_active": True
            },
            {
                "id": 3,
                "name": "Code Assistant",
                "description": "Agent for programming and code-related tasks",
                "agent_type": "code",
                "capabilities": ["code_generation", "code_analysis", "debugging"],
                "config": {"model": "gpt-4", "temperature": 0.2},
                "is_active": True
            },
            {
                "id": 4,
                "name": "Creative Writer",
                "description": "Agent for creative writing and content generation",
                "agent_type": "creative",
                "capabilities": ["content_generation", "storytelling", "brainstorming"],
                "config": {"model": "gpt-4", "temperature": 0.9},
                "is_active": True
            }
        ]

    async def execute_agent(
        self,
        conversation_id: int,
        message: str,
        agent_type: str,
        tools: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an agent with the given parameters."""
        start_time = datetime.utcnow()

        # Create initial agent state
        agent_state = AgentState(
            conversation_id=conversation_id,
            state_data={
                "message": message,
                "agent_type": agent_type,
                "tools": tools or [],
                "context": context or {},
                "start_time": start_time.isoformat()
            },
            current_node="input_processing",
            status="running"
        )
        self.db.add(agent_state)
        self.db.commit()

        try:
            # Build and execute agent graph
            graph = self.graph_builder.build_graph(agent_type)

            # Initialize state for execution
            initial_state = {
                "messages": [{"role": "user", "content": message}],
                "tools": tools or [],
                "context": context or {},
                "agent_type": agent_type,
                "current_node": "input_processing"
            }

            # Execute the graph
            result = await graph.ainvoke(initial_state)

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Update agent state
            agent_state.state_data = result
            agent_state.current_node = "output_synthesis"
            agent_state.status = "completed"
            agent_state.updated_at = datetime.utcnow()
            self.db.commit()

            return {
                "response": result.get("final_response", "No response generated"),
                "execution_time": execution_time,
                "tools_used": result.get("tools_used", []),
                "tokens_used": result.get("tokens_used", 0),
                "agent_state": result
            }

        except Exception as e:
            # Update agent state with error
            agent_state.status = "failed"
            agent_state.error_message = str(e)
            agent_state.updated_at = datetime.utcnow()
            self.db.commit()

            raise e

    def get_agent_state(self, conversation_id: int) -> Optional[AgentState]:
        """Get current agent state for a conversation."""
        return self.db.query(AgentState).filter(
            AgentState.conversation_id == conversation_id
        ).order_by(AgentState.created_at.desc()).first()

    def get_execution_history(self, conversation_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get agent execution history for a conversation."""
        states = self.db.query(AgentState).filter(
            AgentState.conversation_id == conversation_id
        ).order_by(AgentState.created_at.desc()).limit(limit).all()

        return [
            {
                "id": state.id,
                "status": state.status,
                "current_node": state.current_node,
                "state_data": state.state_data,
                "error_message": state.error_message,
                "created_at": state.created_at,
                "updated_at": state.updated_at,
                "execution_time": (state.updated_at - state.created_at).total_seconds() if state.updated_at else None
            }
            for state in states
        ]

    def clear_agent_state(self, conversation_id: int) -> bool:
        """Clear agent state for a conversation."""
        states = self.db.query(AgentState).filter(
            AgentState.conversation_id == conversation_id
        ).all()

        for state in states:
            self.db.delete(state)

        self.db.commit()
        return True

    def stop_execution(self, conversation_id: int) -> bool:
        """Stop current agent execution."""
        state = self.get_agent_state(conversation_id)
        if state and state.status == "running":
            state.status = "stopped"
            state.error_message = "Execution stopped by user"
            state.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def get_agent_stats(self, conversation_id: int) -> Dict[str, Any]:
        """Get agent execution statistics for a conversation."""
        states = self.db.query(AgentState).filter(
            AgentState.conversation_id == conversation_id
        ).all()

        if not states:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0,
                "most_used_agent_types": [],
                "total_tokens_used": 0
            }

        total_executions = len(states)
        successful_executions = len([s for s in states if s.status == "completed"])
        failed_executions = len([s for s in states if s.status == "failed"])

        # Calculate average execution time
        execution_times = []
        for state in states:
            if state.updated_at and state.created_at:
                execution_time = (state.updated_at - state.created_at).total_seconds()
                execution_times.append(execution_time)

        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Get agent type usage
        agent_types = {}
        total_tokens = 0
        for state in states:
            if state.state_data and "agent_type" in state.state_data:
                agent_type = state.state_data["agent_type"]
                agent_types[agent_type] = agent_types.get(agent_type, 0) + 1

            if state.state_data and "tokens_used" in state.state_data:
                total_tokens += state.state_data["tokens_used"]

        most_used_agent_types = [
            {"agent_type": agent_type, "count": count}
            for agent_type, count in sorted(agent_types.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "average_execution_time": avg_execution_time,
            "most_used_agent_types": most_used_agent_types,
            "total_tokens_used": total_tokens,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0
        }

    def validate_agent_config(self, agent_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent configuration."""
        errors = []
        warnings = []

        # Basic validation
        if not agent_type:
            errors.append("Agent type is required")

        if not config:
            warnings.append("No configuration provided, using defaults")

        # Model validation
        if "model" in config:
            model = config["model"]
            if not isinstance(model, str):
                errors.append("Model must be a string")

        # Temperature validation
        if "temperature" in config:
            temperature = config["temperature"]
            if not isinstance(temperature, (int, float)):
                errors.append("Temperature must be a number")
            elif temperature < 0 or temperature > 2:
                errors.append("Temperature must be between 0 and 2")

        # Tools validation
        if "tools" in config:
            tools = config["tools"]
            if not isinstance(tools, list):
                errors.append("Tools must be a list")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }