"""
End-to-end tests for the LangGraph Deep Web Agent system

These tests simulate real user scenarios and verify that the entire
system works correctly from frontend to backend.
"""

import asyncio
import json
import time
import pytest
from typing import Dict, Any
import httpx
import websockets
from playwright.async_api import async_playwright


class TestFullSystemE2E:
    """End-to-end tests for the complete system"""

    @pytest.fixture
    async def browser(self):
        """Create browser instance for E2E testing"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            yield browser
            await browser.close()

    @pytest.fixture
    async def page(self, browser):
        """Create page instance"""
        page = await browser.new_page()
        yield page
        await page.close()

    @pytest.fixture
    async def api_client(self):
        """Create HTTP client for API testing"""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            yield client

    @pytest.fixture
    async def test_user(self, api_client):
        """Create a test user"""
        user_data = {
            "email": "e2e-test@example.com",
            "password": "testpassword123",
            "name": "E2E Test User"
        }

        # Register user
        response = await api_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Login to get token
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }

        response = await api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        login_response = response.json()
        token = login_response["access_token"]

        return {
            "user_data": user_data,
            "token": token,
            "user_id": login_response["user_id"]
        }

    @pytest.mark.asyncio
    async def test_complete_user_workflow(self, page, api_client, test_user):
        """Test complete user workflow from registration to agent interaction"""
        # Navigate to application
        await page.goto("http://localhost:3000")

        # Verify page loads
        assert await page.title() == "Deep Agent"

        # Login
        await page.fill("#email", test_user["user_data"]["email"])
        await page.fill("#password", test_user["user_data"]["password"])
        await page.click("#login-button")

        # Wait for dashboard
        await page.wait_for_selector("#dashboard", timeout=10000)

        # Verify user is logged in
        assert await page.is_visible("#user-menu")

        # Start new conversation
        await page.click("#new-conversation")
        await page.wait_for_selector("#chat-interface", timeout=5000)

        # Send test message
        test_message = "Hello, I need help analyzing some data"
        await page.fill("#message-input", test_message)
        await page.click("#send-button")

        # Wait for response
        await page.wait_for_selector(".message-response", timeout=15000)

        # Verify response
        response_element = await page.query_selector(".message-response")
        response_text = await response_element.text_content()
        assert len(response_text) > 0

        # Test agent execution
        await page.click("#agent-tools")
        await page.click("#data-analysis-tool")

        # Configure tool parameters
        await page.fill("#data-source", "https://example.com/data.csv")
        await page.click("#execute-tool")

        # Wait for execution result
        await page.wait_for_selector("#execution-result", timeout=10000)

        # Verify execution result
        result_element = await page.query_selector("#execution-result")
        assert result_element is not None

        # Check conversation history
        await page.click("#conversation-history")
        await page.wait_for_selector(".conversation-item", timeout=5000)

        # Verify conversation is saved
        conversation_items = await page.query_selector_all(".conversation-item")
        assert len(conversation_items) > 0

    @pytest.mark.asyncio
    async def test_websocket_real_time_communication(self, test_user):
        """Test WebSocket real-time communication"""
        uri = "ws://localhost:8000/ws/chat"
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        messages_received = []

        async with websockets.connect(uri, extra_headers=headers) as websocket:
            # Send initial message
            initial_message = {
                "type": "chat",
                "message": "WebSocket test message",
                "user_id": test_user["user_id"],
                "session_id": "test-session-e2e"
            }

            await websocket.send(json.dumps(initial_message))

            # Listen for responses
            async for message in websocket:
                response = json.loads(message)
                messages_received.append(response)

                if len(messages_received) >= 3:
                    break

        # Verify messages received
        assert len(messages_received) >= 3

        # Verify message structure
        for msg in messages_received:
            assert "type" in msg
            assert "message" in msg
            assert "timestamp" in msg

    @pytest.mark.asyncio
    async def test_agent_execution_workflow(self, api_client, test_user):
        """Test complete agent execution workflow"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Start agent execution
        execution_request = {
            "task": "Analyze the following data and provide insights",
            "context": {
                "user_id": test_user["user_id"],
                "session_id": "test-execution-session",
                "priority": "normal"
            },
            "tools": ["data_analysis", "web_search"],
            "parameters": {
                "data_sources": ["https://example.com/data.csv"],
                "analysis_type": "comprehensive"
            }
        }

        response = await api_client.post(
            "/api/v1/agent/execute",
            json=execution_request,
            headers=headers
        )
        assert response.status_code == 200

        execution_data = response.json()
        execution_id = execution_data["execution_id"]

        # Monitor execution progress
        max_attempts = 30
        attempts = 0

        while attempts < max_attempts:
            status_response = await api_client.get(
                f"/api/v1/agent/execution/{execution_id}",
                headers=headers
            )
            assert status_response.status_code == 200

            status_data = status_response.json()

            if status_data["status"] == "completed":
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Agent execution failed: {status_data.get('error', 'Unknown error')}")

            await asyncio.sleep(2)
            attempts += 1

        # Verify execution completed
        assert attempts < max_attempts

        # Get execution results
        result_response = await api_client.get(
            f"/api/v1/agent/execution/{execution_id}/result",
            headers=headers
        )
        assert result_response.status_code == 200

        result_data = result_response.json()
        assert "result" in result_data
        assert "insights" in result_data["result"]
        assert "tools_used" in result_data["result"]

    @pytest.mark.asyncio
    async def test_memory_persistence(self, api_client, test_user):
        """Test memory persistence across sessions"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Store memory
        memory_data = {
            "content": {
                "preferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                }
            },
            "type": "user_preferences",
            "source": "user_explicit"
        }

        response = await api_client.post(
            f"/api/v1/memory/{test_user['user_id']}",
            json=memory_data,
            headers=headers
        )
        assert response.status_code == 200

        # Retrieve memory
        get_response = await api_client.get(
            f"/api/v1/memory/{test_user['user_id']}/user_preferences",
            headers=headers
        )
        assert get_response.status_code == 200

        retrieved_memory = get_response.json()
        assert retrieved_memory["content"] == memory_data["content"]

        # Update memory
        updated_memory = memory_data.copy()
        updated_memory["content"]["preferences"]["theme"] = "light"

        update_response = await api_client.put(
            f"/api/v1/memory/{test_user['user_id']}/user_preferences",
            json=updated_memory,
            headers=headers
        )
        assert update_response.status_code == 200

        # Verify update
        get_updated_response = await api_client.get(
            f"/api/v1/memory/{test_user['user_id']}/user_preferences",
            headers=headers
        )
        assert get_updated_response.status_code == 200

        updated_data = get_updated_response.json()
        assert updated_data["content"]["preferences"]["theme"] == "light"

    @pytest.mark.asyncio
    async def test_multi_tool_execution(self, api_client, test_user):
        """Test execution of multiple tools in sequence"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Execute web search
        search_request = {
            "tool": "web_search",
            "parameters": {
                "query": "artificial intelligence trends 2024",
                "limit": 5
            }
        }

        search_response = await api_client.post(
            "/api/v1/tools/execute",
            json=search_request,
            headers=headers
        )
        assert search_response.status_code == 200

        search_result = search_response.json()
        assert search_result["success"] is True
        assert "results" in search_result

        # Execute data analysis
        analysis_request = {
            "tool": "data_analysis",
            "parameters": {
                "data": search_result["results"],
                "analysis_type": "sentiment"
            }
        }

        analysis_response = await api_client.post(
            "/api/v1/tools/execute",
            json=analysis_request,
            headers=headers
        )
        assert analysis_response.status_code == 200

        analysis_result = analysis_response.json()
        assert analysis_result["success"] is True
        assert "analysis" in analysis_result

        # Execute report generation
        report_request = {
            "tool": "report_generator",
            "parameters": {
                "title": "AI Trends Analysis",
                "content": {
                    "search_results": search_result["results"],
                    "analysis": analysis_result["analysis"]
                },
                "format": "pdf"
            }
        }

        report_response = await api_client.post(
            "/api/v1/tools/execute",
            json=report_request,
            headers=headers
        )
        assert report_response.status_code == 200

        report_result = report_response.json()
        assert report_result["success"] is True
        assert "report_url" in report_result

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, api_client, test_user):
        """Test error handling and recovery mechanisms"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Test with invalid tool
        invalid_tool_request = {
            "tool": "nonexistent_tool",
            "parameters": {"test": "value"}
        }

        response = await api_client.post(
            "/api/v1/tools/execute",
            json=invalid_tool_request,
            headers=headers
        )
        assert response.status_code == 404

        # Test with invalid parameters
        invalid_params_request = {
            "tool": "web_search",
            "parameters": {"invalid": "params"}
        }

        response = await api_client.post(
            "/api/v1/tools/execute",
            json=invalid_params_request,
            headers=headers
        )
        assert response.status_code == 400

        # Test rate limiting
        for i in range(15):  # Exceed rate limit
            await api_client.get("/health", headers=headers)

        response = await api_client.get("/api/v1/chat", headers=headers)
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_performance_under_load(self, api_client, test_user):
        """Test system performance under load"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Create concurrent requests
        tasks = []
        start_time = time.time()

        for i in range(10):
            task = api_client.post(
                "/api/v1/chat",
                json={
                    "message": f"Load test message {i}",
                    "user_id": test_user["user_id"],
                    "session_id": f"load-test-session-{i}"
                },
                headers=headers
            )
            tasks.append(task)

        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify all requests completed
        assert len(responses) == 10

        # Verify performance (should complete within 10 seconds)
        assert execution_time < 10.0

        # Verify all responses are successful
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                pytest.fail(f"Request {i} failed with exception: {response}")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_data_export_and_import(self, api_client, test_user):
        """Test data export and import functionality"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Create test data
        test_conversations = []
        for i in range(3):
            chat_data = {
                "message": f"Test conversation {i}",
                "user_id": test_user["user_id"],
                "session_id": f"export-test-session-{i}"
            }

            response = await api_client.post("/api/v1/chat", json=chat_data, headers=headers)
            assert response.status_code == 200
            test_conversations.append(response.json())

        # Export data
        export_response = await api_client.get(
            f"/api/v1/user/{test_user['user_id']}/export",
            headers=headers
        )
        assert export_response.status_code == 200

        export_data = export_response.json()
        assert "conversations" in export_data
        assert "memories" in export_data
        assert "preferences" in export_data

        # Verify exported data
        assert len(export_data["conversations"]) >= 3

        # Import data (test with different user)
        import_user_data = {
            "email": "import-test@example.com",
            "password": "testpassword123",
            "name": "Import Test User"
        }

        register_response = await api_client.post("/api/v1/auth/register", json=import_user_data)
        assert register_response.status_code == 200

        login_response = await api_client.post("/api/v1/auth/login", json={
            "email": import_user_data["email"],
            "password": import_user_data["password"]
        })
        assert login_response.status_code == 200

        import_token = login_response.json()["access_token"]
        import_user_id = login_response.json()["user_id"]

        import_headers = {"Authorization": f"Bearer {import_token}"}

        # Import exported data
        import_response = await api_client.post(
            f"/api/v1/user/{import_user_id}/import",
            json=export_data,
            headers=import_headers
        )
        assert import_response.status_code == 200

        # Verify imported data
        verify_response = await api_client.get(
            f"/api/v1/user/{import_user_id}/conversations",
            headers=import_headers
        )
        assert verify_response.status_code == 200

        imported_conversations = verify_response.json()
        assert len(imported_conversations) >= 3

    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, api_client):
        """Test system health monitoring"""
        # Check overall system health
        response = await api_client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "services" in health_data

        # Check individual service health
        services = health_data["services"]
        for service_name, service_status in services.items():
            assert "status" in service_status
            assert "response_time" in service_status

        # Check API health
        api_response = await api_client.get("/api/v1/health")
        assert api_response.status_code == 200

        api_health = api_response.json()
        assert api_health["status"] == "healthy"

        # Check database health
        db_response = await api_client.get("/api/v1/health/database")
        assert db_response.status_code == 200

        db_health = db_response.json()
        assert db_health["status"] == "healthy"

        # Check Redis health
        redis_response = await api_client.get("/api/v1/health/redis")
        assert redis_response.status_code == 200

        redis_health = redis_response.json()
        assert redis_health["status"] == "healthy"


@pytest.mark.e2e
class TestProductionScenarios:
    """Production scenario tests"""

    @pytest.mark.asyncio
    async def test_high_volume_conversation_scenario(self, api_client, test_user):
        """Test high volume conversation scenario"""
        # Simulate a user having many conversations
        pass

    @pytest.mark.asyncio
    async def test_multi_user_collaboration_scenario(self, api_client):
        """Test multi-user collaboration scenario"""
        # Simulate multiple users collaborating
        pass

    @pytest.mark.asyncio
    async def test_long_running_agent_task_scenario(self, api_client, test_user):
        """Test long-running agent task scenario"""
        # Test agents that run for extended periods
        pass