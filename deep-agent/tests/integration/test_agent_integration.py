"""
Integration tests for the LangGraph Deep Web Agent system

These tests verify that all components work together correctly
and that the agent can perform end-to-end tasks.
"""

import pytest
import asyncio
import json
import httpx
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.core.agent import AgentOrchestrator
from app.core.memory import MemoryManager
from app.core.tools import ToolRegistry
from app.core.security import SecurityManager
from app.models.conversation import Conversation
from app.models.memory import Memory
from app.models.session import Session
from tests.utils.database import get_test_db
from tests.utils.redis import get_test_redis


class TestAgentIntegration:
    """Integration tests for the agent system"""

    @pytest.fixture
    async def test_client(self):
        """Create a test HTTP client"""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            yield client

    @pytest.fixture
    async def test_db(self):
        """Create test database session"""
        async for session in get_test_db():
            yield session

    @pytest.fixture
    async def test_redis(self):
        """Create test Redis connection"""
        async for redis in get_test_redis():
            yield redis

    @pytest.fixture
    async def agent_orchestrator(self):
        """Create agent orchestrator instance"""
        orchestrator = AgentOrchestrator()
        yield orchestrator
        await orchestrator.cleanup()

    @pytest.fixture
    async def memory_manager(self, test_db, test_redis):
        """Create memory manager instance"""
        manager = MemoryManager(test_db, test_redis)
        yield manager

    @pytest.fixture
    async def tool_registry(self):
        """Create tool registry instance"""
        registry = ToolRegistry()
        yield registry
        await registry.cleanup()

    @pytest.fixture
    async def security_manager(self, test_db):
        """Create security manager instance"""
        manager = SecurityManager(test_db)
        yield manager

    @pytest.fixture
    async def test_session(self, test_db):
        """Create a test session"""
        session = Session(
            session_id="test-session-integration",
            user_id="test-user-integration",
            metadata={"test": True}
        )
        test_db.add(session)
        await test_db.commit()
        return session

    @pytest.mark.asyncio
    async def test_agent_full_workflow(self, agent_orchestrator, memory_manager, tool_registry, test_session):
        """Test complete agent workflow from input to output"""
        # Initialize agent components
        await agent_orchestrator.initialize()
        await memory_manager.initialize()
        await tool_registry.initialize()

        # Test input
        input_data = {
            "message": "What is the current weather in New York?",
            "user_id": test_session.user_id,
            "session_id": test_session.session_id,
            "context": {
                "previous_messages": [],
                "user_preferences": {"temperature_unit": "celsius"}
            }
        }

        # Execute agent workflow
        result = await agent_orchestrator.execute_workflow(input_data)

        # Verify result structure
        assert result is not None
        assert "response" in result
        assert "execution_id" in result
        assert "timestamp" in result
        assert "tools_used" in result
        assert "memory_updated" in result

        # Verify memory integration
        memory = await memory_manager.get_memory(test_session.user_id, "weather_preference")
        assert memory is not None
        assert "temperature_unit" in memory.content

        # Verify tool usage
        assert len(result["tools_used"]) > 0
        assert any("weather" in tool for tool in result["tools_used"])

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self, agent_orchestrator, test_session):
        """Test concurrent agent execution"""
        await agent_orchestrator.initialize()

        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            input_data = {
                "message": f"Test message {i}",
                "user_id": test_session.user_id,
                "session_id": test_session.session_id,
                "context": {"iteration": i}
            }
            tasks.append(agent_orchestrator.execute_workflow(input_data))

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all tasks completed
        assert len(results) == 5
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed: {result}"
            assert result["execution_id"] is not None

    @pytest.mark.asyncio
    async def test_memory_integration(self, memory_manager, test_session):
        """Test memory system integration"""
        await memory_manager.initialize()

        # Store memory
        memory_data = {
            "content": {"preference": "dark_mode", "value": True},
            "type": "preference",
            "source": "user_explicit"
        }

        await memory_manager.store_memory(
            test_session.user_id,
            "ui_preference",
            memory_data,
            metadata={"session_id": test_session.session_id}
        )

        # Retrieve memory
        retrieved_memory = await memory_manager.get_memory(test_session.user_id, "ui_preference")
        assert retrieved_memory is not None
        assert retrieved_memory.content == memory_data

        # Test memory search
        search_results = await memory_manager.search_memories(
            test_session.user_id,
            "preference",
            limit=10
        )
        assert len(search_results) > 0

    @pytest.mark.asyncio
    async def test_tool_integration(self, tool_registry):
        """Test tool system integration"""
        await tool_registry.initialize()

        # Get available tools
        tools = await tool_registry.get_available_tools()
        assert len(tools) > 0

        # Test tool execution
        tool_name = "web_search"
        tool_params = {"query": "test search", "limit": 5}

        result = await tool_registry.execute_tool(tool_name, tool_params)
        assert result is not None
        assert "success" in result
        assert "data" in result

        # Test tool validation
        invalid_params = {"invalid_param": "value"}
        validation_result = await tool_registry.validate_tool_params(tool_name, invalid_params)
        assert validation_result["valid"] is False

    @pytest.mark.asyncio
    async def test_security_integration(self, security_manager, test_session):
        """Test security system integration"""
        # Test session validation
        is_valid = await security_manager.validate_session(test_session.session_id, test_session.user_id)
        assert is_valid is True

        # Test permission check
        has_permission = await security_manager.check_permission(
            test_session.user_id,
            "agent.execute",
            {"session_id": test_session.session_id}
        )
        assert has_permission is True

        # Test rate limiting
        rate_limited = await security_manager.check_rate_limit(
            test_session.user_id,
            "api_request",
            limit=10,
            window=60
        )
        assert rate_limited["allowed"] is True

    @pytest.mark.asyncio
    async def test_api_integration(self, test_client, test_session):
        """Test API endpoint integration"""
        # Test health endpoint
        response = await test_client.get("/health")
        assert response.status_code == 200

        # Test chat endpoint
        chat_data = {
            "message": "Hello, I need help with something",
            "user_id": test_session.user_id,
            "session_id": test_session.session_id
        }

        response = await test_client.post(
            "/api/v1/chat",
            json=chat_data,
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        chat_response = response.json()
        assert "response_id" in chat_response
        assert "response" in chat_response
        assert "timestamp" in chat_response

        # Test agent execution endpoint
        agent_data = {
            "task": "Analyze the provided data",
            "context": {
                "user_id": test_session.user_id,
                "session_id": test_session.session_id
            },
            "tools": ["data_analysis"]
        }

        response = await test_client.post(
            "/api/v1/agent/execute",
            json=agent_data,
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        agent_response = response.json()
        assert "execution_id" in agent_response
        assert "status" in agent_response

    @pytest.mark.asyncio
    async def test_websocket_integration(self, test_session):
        """Test WebSocket integration"""
        import websockets
        import json

        uri = f"ws://localhost:8000/ws/chat"
        headers = {"Authorization": "Bearer test-token"}

        async with websockets.connect(uri, extra_headers=headers) as websocket:
            # Send test message
            message = {
                "type": "chat",
                "message": "WebSocket test message",
                "user_id": test_session.user_id,
                "session_id": test_session.session_id
            }

            await websocket.send(json.dumps(message))

            # Receive response
            response = await websocket.recv()
            response_data = json.loads(response)

            assert "type" in response_data
            assert "message" in response_data
            assert "timestamp" in response_data

            # Test multiple messages
            for i in range(3):
                follow_up = {
                    "type": "follow_up",
                    "message": f"Follow-up message {i}",
                    "user_id": test_session.user_id,
                    "session_id": test_session.session_id
                }

                await websocket.send(json.dumps(follow_up))
                response = await websocket.recv()
                response_data = json.loads(response)

                assert response_data["type"] in ["chat", "follow_up"]

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, agent_orchestrator, test_session):
        """Test error handling across integrated components"""
        await agent_orchestrator.initialize()

        # Test with invalid input
        invalid_input = {
            "message": "",  # Empty message
            "user_id": test_session.user_id,
            "session_id": test_session.session_id
        }

        with pytest.raises(ValueError) as exc_info:
            await agent_orchestrator.execute_workflow(invalid_input)
        assert "message" in str(exc_info.value).lower()

        # Test with missing required fields
        incomplete_input = {
            "message": "Test message"
            # Missing user_id and session_id
        }

        with pytest.raises(KeyError) as exc_info:
            await agent_orchestrator.execute_workflow(incomplete_input)
        assert "user_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_performance_integration(self, agent_orchestrator, test_session):
        """Test performance metrics across integrated components"""
        await agent_orchestrator.initialize()

        import time
        start_time = time.time()

        # Execute multiple requests
        tasks = []
        for i in range(10):
            input_data = {
                "message": f"Performance test message {i}",
                "user_id": test_session.user_id,
                "session_id": test_session.session_id
            }
            tasks.append(agent_orchestrator.execute_workflow(input_data))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Verify performance
        execution_time = end_time - start_time
        assert execution_time < 30.0  # Should complete within 30 seconds

        # Verify all results are valid
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Task {i} failed"
            assert result["execution_time"] < 5.0  # Each task should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_data_consistency_integration(self, memory_manager, test_session, test_db):
        """Test data consistency across components"""
        await memory_manager.initialize()

        # Store data through memory manager
        test_data = {
            "content": {"test_key": "test_value"},
            "type": "test_data",
            "source": "integration_test"
        }

        await memory_manager.store_memory(
            test_session.user_id,
            "test_memory",
            test_data,
            metadata={"session_id": test_session.session_id}
        )

        # Verify in database
        db_memory = await test_db.query(Memory).filter(
            Memory.user_id == test_session.user_id,
            Memory.memory_id == "test_memory"
        ).first()

        assert db_memory is not None
        assert db_memory.content == test_data

        # Verify in Redis cache
        cached_memory = await memory_manager.get_memory(test_session.user_id, "test_memory")
        assert cached_memory is not None
        assert cached_memory.content == test_data

        # Test cache invalidation
        await memory_manager.invalidate_cache(test_session.user_id, "test_memory")
        cached_after_invalidation = await memory_manager.get_memory(
            test_session.user_id,
            "test_memory"
        )
        assert cached_after_invalidation is None


@pytest.mark.integration
class TestSystemIntegration:
    """System-wide integration tests"""

    @pytest.mark.asyncio
    async def test_full_system_workflow(self):
        """Test complete system workflow from user input to final output"""
        # This test simulates a real user interaction flow
        pass

    @pytest.mark.asyncio
    async def test_system_recovery(self):
        """Test system recovery from failures"""
        # Test how the system handles and recovers from various failures
        pass

    @pytest.mark.asyncio
    async def test_system_scaling(self):
        """Test system behavior under load"""
        # Test how the system scales with increased load
        pass