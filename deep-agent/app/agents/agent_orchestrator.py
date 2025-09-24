import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from langgraph.graph import Graph, END
from langgraph.prebuilt import ToolExecutor
from app.services.cache_service import cache_service
from app.services.session_service import session_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AgentState:
    """
    Enhanced agent state management for LangGraph
    """

    def __init__(
        self,
        conversation_id: int,
        user_id: int,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[str]] = None,
        max_iterations: int = 50,
        timeout: int = 300
    ):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.message = message
        self.context = context or {}
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.timeout = timeout

        # Execution state
        self.current_node = "input_processing"
        self.iteration_count = 0
        self.start_time = datetime.utcnow()
        self.status = "pending"

        # Data storage
        self.input_data = {}
        self.planning_data = {}
        self.execution_data = {}
        self.memory_data = {}
        self.output_data = {}

        # Results and tracking
        self.results = []
        self.errors = []
        self.tools_used = []
        self.execution_path = []

        # Cache keys
        self.state_cache_key = f"agent_state:{conversation_id}:{uuid.uuid4().hex[:8]}"
        self.context_cache_key = f"agent_context:{conversation_id}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for storage"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "message": self.message,
            "context": self.context,
            "tools": self.tools,
            "max_iterations": self.max_iterations,
            "timeout": self.timeout,
            "current_node": self.current_node,
            "iteration_count": self.iteration_count,
            "start_time": self.start_time.isoformat(),
            "status": self.status,
            "input_data": self.input_data,
            "planning_data": self.planning_data,
            "execution_data": self.execution_data,
            "memory_data": self.memory_data,
            "output_data": self.output_data,
            "results": self.results,
            "errors": self.errors,
            "tools_used": self.tools_used,
            "execution_path": self.execution_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create state from dictionary"""
        state = cls(
            conversation_id=data["conversation_id"],
            user_id=data["user_id"],
            message=data["message"],
            context=data.get("context", {}),
            tools=data.get("tools", []),
            max_iterations=data.get("max_iterations", 50),
            timeout=data.get("timeout", 300)
        )

        state.current_node = data.get("current_node", "input_processing")
        state.iteration_count = data.get("iteration_count", 0)
        state.start_time = datetime.fromisoformat(data["start_time"])
        state.status = data.get("status", "pending")
        state.input_data = data.get("input_data", {})
        state.planning_data = data.get("planning_data", {})
        state.execution_data = data.get("execution_data", {})
        state.memory_data = data.get("memory_data", {})
        state.output_data = data.get("output_data", {})
        state.results = data.get("results", [])
        state.errors = data.get("errors", [])
        state.tools_used = data.get("tools_used", [])
        state.execution_path = data.get("execution_path", [])

        return state

    async def save_to_cache(self):
        """Save state to cache"""
        await cache_service.set(
            self.state_cache_key,
            self.to_dict(),
            ttl=self.timeout
        )

    async def load_from_cache(self):
        """Load state from cache"""
        data = await cache_service.get(self.state_cache_key)
        if data:
            loaded_state = AgentState.from_dict(data)
            self.__dict__.update(loaded_state.__dict__)
            return True
        return False

    async def update_status(self, status: str):
        """Update execution status"""
        self.status = status
        await self.save_to_cache()

    async def add_result(self, result: Dict[str, Any]):
        """Add execution result"""
        self.results.append(result)
        await self.save_to_cache()

    async def add_error(self, error: str, node: Optional[str] = None):
        """Add execution error"""
        error_data = {
            "error": error,
            "node": node or self.current_node,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.errors.append(error_data)
        await self.save_to_cache()

    async def track_execution(self, node: str, data: Dict[str, Any] = None):
        """Track execution path"""
        self.execution_path.append({
            "node": node,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        })
        await self.save_to_cache()

    async def get_execution_time(self) -> float:
        """Get current execution time in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()

    async def should_continue(self) -> bool:
        """Check if execution should continue"""
        if self.iteration_count >= self.max_iterations:
            return False
        if await self.get_execution_time() >= self.timeout:
            return False
        if self.status in ["completed", "failed", "stopped"]:
            return False
        return True


class AgentOrchestrator:
    """
    Enhanced LangGraph orchestrator for AI agent execution
    """

    def __init__(self):
        self.graph = Graph()
        self.tool_executor = ToolExecutor()
        self.agents = {}
        self.tools = {}
        self._setup_graph()

    def _setup_graph(self):
        """Setup LangGraph workflow"""
        # Define nodes
        self.graph.add_node("input_processing", self._process_input)
        self.graph.add_node("task_planning", self._plan_tasks)
        self.graph.add_node("tool_selection", self._select_tools)
        self.graph.add_node("execution", self._execute_tools)
        self.graph.add_node("memory_management", self._manage_memory)
        self.graph.add_node("output_synthesis", self._synthesize_output)
        self.graph.add_node("error_handling", self._handle_errors)

        # Define edges
        self.graph.add_edge("input_processing", "task_planning")
        self.graph.add_edge("task_planning", "tool_selection")
        self.graph.add_edge("tool_selection", "execution")
        self.graph.add_edge("execution", "memory_management")
        self.graph.add_edge("memory_management", "output_synthesis")

        # Conditional edges
        self.graph.add_conditional_edges(
            "input_processing",
            self._should_continue_execution,
            {
                "continue": "task_planning",
                "error": "error_handling",
                "end": END
            }
        )

        self.graph.add_conditional_edges(
            "execution",
            self._should_continue_execution,
            {
                "continue": "memory_management",
                "error": "error_handling",
                "end": END
            }
        )

        self.graph.add_conditional_edges(
            "output_synthesis",
            self._should_continue_execution,
            {
                "continue": "input_processing",  # For multi-turn conversations
                "end": END
            }
        )

        # Set entry point
        self.graph.set_entry_point("input_processing")

    def register_agent(self, name: str, agent_instance: Any):
        """Register an agent instance"""
        self.agents[name] = agent_instance

    def register_tool(self, name: str, tool_instance: Any):
        """Register a tool instance"""
        self.tools[name] = tool_instance

    async def execute_agent(
        self,
        conversation_id: int,
        user_id: int,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[str]] = None,
        max_iterations: int = 50,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute agent with given parameters
        """
        try:
            # Initialize agent state
            state = AgentState(
                conversation_id=conversation_id,
                user_id=user_id,
                message=message,
                context=context,
                tools=tools,
                max_iterations=max_iterations,
                timeout=timeout
            )

            await state.update_status("running")
            await state.save_to_cache()

            # Load conversation context
            await self._load_conversation_context(state)

            # Execute graph
            result = await self._execute_graph(state)

            # Save final state
            await state.update_status("completed")
            await state.add_result(result)

            # Store in conversation history
            await self._store_execution_result(state, result)

            return result

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            if 'state' in locals():
                await state.add_error(str(e))
                await state.update_status("failed")
            raise

    async def _execute_graph(self, state: AgentState) -> Dict[str, Any]:
        """Execute the LangGraph workflow"""
        logger.info(f"Starting agent execution for conversation {state.conversation_id}")

        try:
            # Execute the graph
            async for node_result in self.graph.astream(state.to_dict()):
                node_name = node_result.get("node", "")
                node_data = node_result.get("data", {})

                # Update state
                state.current_node = node_name
                state.iteration_count += 1
                await state.track_execution(node_name, node_data)

                # Check timeout and iterations
                if not await state.should_continue():
                    break

                # Update state with node results
                if node_data:
                    await self._update_state_from_node(state, node_name, node_data)

                # Send progress update via WebSocket
                await self._send_progress_update(state)

            # Generate final result
            result = await self._generate_final_result(state)
            return result

        except asyncio.TimeoutError:
            logger.error(f"Agent execution timeout for conversation {state.conversation_id}")
            await state.add_error("Execution timeout")
            return {"error": "Execution timeout", "status": "timeout"}
        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            await state.add_error(str(e))
            return {"error": str(e), "status": "error"}

    async def _process_input(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Process input node"""
        state = AgentState.from_dict(state_dict)

        # Parse and validate input
        input_data = {
            "original_message": state.message,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": state.user_id,
            "intent_analysis": await self._analyze_intent(state.message),
            "entities": await self._extract_entities(state.message),
            "context": state.context
        }

        state.input_data = input_data
        await state.save_to_cache()

        return {"node": "input_processing", "data": input_data}

    async def _plan_tasks(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Plan tasks node"""
        state = AgentState.from_dict(state_dict)

        # Generate execution plan
        planning_data = {
            "primary_goal": await self._identify_primary_goal(state),
            "subtasks": await self._generate_subtasks(state),
            "execution_strategy": await self._determine_strategy(state),
            "estimated_steps": len(state.tools or []),
            "complexity_score": await self._assess_complexity(state)
        }

        state.planning_data = planning_data
        await state.save_to_cache()

        return {"node": "task_planning", "data": planning_data}

    async def _select_tools(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Select tools node"""
        state = AgentState.from_dict(state_dict)

        # Select appropriate tools
        selected_tools = []
        tool_reasoning = []

        for tool_name in state.tools:
            if await self._should_use_tool(state, tool_name):
                selected_tools.append(tool_name)
                tool_reasoning.append({
                    "tool": tool_name,
                    "reason": await self._explain_tool_selection(state, tool_name)
                })

        state.tools = selected_tools
        state.execution_data["selected_tools"] = selected_tools
        state.execution_data["tool_reasoning"] = tool_reasoning
        await state.save_to_cache()

        return {"node": "tool_selection", "data": {"selected_tools": selected_tools}}

    async def _execute_tools(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tools node"""
        state = AgentState.from_dict(state_dict)

        execution_results = []
        for tool_name in state.tools:
            try:
                tool_result = await self._execute_single_tool(state, tool_name)
                execution_results.append({
                    "tool": tool_name,
                    "result": tool_result,
                    "success": True
                })
                state.tools_used.append(tool_name)
            except Exception as e:
                execution_results.append({
                    "tool": tool_name,
                    "error": str(e),
                    "success": False
                })

        state.execution_data["tool_results"] = execution_results
        await state.save_to_cache()

        return {"node": "execution", "data": {"execution_results": execution_results}}

    async def _manage_memory(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Manage memory node"""
        state = AgentState.from_dict(state_dict)

        # Update conversation memory
        memory_data = {
            "conversation_summary": await self._generate_conversation_summary(state),
            "key_learnings": await self._extract_key_learnings(state),
            "user_preferences": await self._update_user_preferences(state),
            "context_updates": await self._update_context(state)
        }

        state.memory_data = memory_data
        await state.save_to_cache()

        return {"node": "memory_management", "data": memory_data}

    async def _synthesize_output(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize output node"""
        state = AgentState.from_dict(state_dict)

        # Generate final response
        output_data = {
            "response": await self._generate_response(state),
            "confidence": await self._calculate_confidence(state),
            "follow_up_suggestions": await self._generate_follow_up(state),
            "sources": await self._extract_sources(state),
            "metadata": {
                "execution_time": await state.get_execution_time(),
                "tools_used": state.tools_used,
                "iteration_count": state.iteration_count
            }
        }

        state.output_data = output_data
        await state.save_to_cache()

        return {"node": "output_synthesis", "data": output_data}

    async def _handle_errors(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors node"""
        state = AgentState.from_dict(state_dict)

        error_handling = {
            "error_analysis": await self._analyze_errors(state),
            "recovery_strategy": await self._determine_recovery(state),
            "fallback_response": await self._generate_fallback(state)
        }

        return {"node": "error_handling", "data": error_handling}

    # Helper methods
    async def _should_continue_execution(self, state_dict: Dict[str, Any]) -> str:
        """Determine if execution should continue"""
        state = AgentState.from_dict(state_dict)
        if await state.should_continue():
            return "continue"
        elif state.errors:
            return "error"
        else:
            return "end"

    async def _update_state_from_node(self, state: AgentState, node_name: str, node_data: Dict[str, Any]):
        """Update state based on node results"""
        if node_name == "input_processing":
            state.input_data = node_data
        elif node_name == "task_planning":
            state.planning_data = node_data
        elif node_name == "execution":
            state.execution_data.update(node_data)
        elif node_name == "memory_management":
            state.memory_data = node_data
        elif node_name == "output_synthesis":
            state.output_data = node_data

        await state.save_to_cache()

    async def _generate_final_result(self, state: AgentState) -> Dict[str, Any]:
        """Generate final execution result"""
        return {
            "status": "success",
            "response": state.output_data.get("response", ""),
            "confidence": state.output_data.get("confidence", 0.0),
            "tools_used": state.tools_used,
            "execution_time": await state.get_execution_time(),
            "iteration_count": state.iteration_count,
            "metadata": {
                "conversation_id": state.conversation_id,
                "user_id": state.user_id,
                "execution_path": state.execution_path,
                "error_count": len(state.errors)
            }
        }

    # Abstract methods to be implemented by specific agents
    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent"""
        # Implementation depends on specific agent type
        return {"intent": "general", "confidence": 0.8}

    async def _extract_entities(self, message: str) -> List[Dict[str, Any]]:
        """Extract entities from message"""
        # Implementation depends on specific agent type
        return []

    async def _identify_primary_goal(self, state: AgentState) -> str:
        """Identify primary execution goal"""
        return "process_user_request"

    async def _generate_subtasks(self, state: AgentState) -> List[Dict[str, Any]]:
        """Generate subtasks for execution"""
        return []

    async def _determine_strategy(self, state: AgentState) -> str:
        """Determine execution strategy"""
        return "sequential"

    async def _assess_complexity(self, state: AgentState) -> float:
        """Assess task complexity"""
        return 0.5

    async def _should_use_tool(self, state: AgentState, tool_name: str) -> bool:
        """Determine if tool should be used"""
        return tool_name in state.tools

    async def _explain_tool_selection(self, state: AgentState, tool_name: str) -> str:
        """Explain why tool was selected"""
        return f"Tool {tool_name} is relevant to the request"

    async def _execute_single_tool(self, state: AgentState, tool_name: str) -> Any:
        """Execute a single tool"""
        if tool_name in self.tools:
            return await self.tools[tool_name].execute(state)
        else:
            raise ValueError(f"Tool {tool_name} not found")

    async def _generate_conversation_summary(self, state: AgentState) -> str:
        """Generate conversation summary"""
        return ""

    async def _extract_key_learnings(self, state: AgentState) -> List[str]:
        """Extract key learnings"""
        return []

    async def _update_user_preferences(self, state: AgentState) -> Dict[str, Any]:
        """Update user preferences"""
        return {}

    async def _update_context(self, state: AgentState) -> Dict[str, Any]:
        """Update conversation context"""
        return {}

    async def _generate_response(self, state: AgentState) -> str:
        """Generate final response"""
        return ""

    async def _calculate_confidence(self, state: AgentState) -> float:
        """Calculate response confidence"""
        return 0.8

    async def _generate_follow_up(self, state: AgentState) -> List[str]:
        """Generate follow-up suggestions"""
        return []

    async def _extract_sources(self, state: AgentState) -> List[Dict[str, Any]]:
        """Extract information sources"""
        return []

    async def _analyze_errors(self, state: AgentState) -> Dict[str, Any]:
        """Analyze execution errors"""
        return {}

    async def _determine_recovery(self, state: AgentState) -> str:
        """Determine recovery strategy"""
        return "retry"

    async def _generate_fallback(self, state: AgentState) -> str:
        """Generate fallback response"""
        return "I apologize, but I encountered an error processing your request."

    async def _load_conversation_context(self, state: AgentState):
        """Load conversation context from cache"""
        context_data = await cache_service.get(state.context_cache_key)
        if context_data:
            state.context.update(context_data)

    async def _store_execution_result(self, state: AgentState, result: Dict[str, Any]):
        """Store execution result in conversation context"""
        updated_context = state.context.copy()
        updated_context["last_execution"] = result
        await cache_service.set(state.context_cache_key, updated_context, ttl=3600)

    async def _send_progress_update(self, state: AgentState):
        """Send progress update via WebSocket"""
        # Implementation depends on WebSocket manager
        pass


# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()