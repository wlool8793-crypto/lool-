"""
Tool service for the Deep Agent application.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
from app.models import ToolExecution
from app.core.redis import redis_manager


class ToolService:
    """Service for tool management and execution."""

    def __init__(self, db: Session):
        self.db = db
        self.available_tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available tools."""
        return {
            "web_search": {
                "name": "web_search",
                "description": "Search the web for information",
                "category": "information",
                "version": "1.0.0",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                },
                "is_active": True,
                "requires_auth": False,
                "rate_limit": 10
            },
            "file_read": {
                "name": "file_read",
                "description": "Read and analyze file contents",
                "category": "file",
                "version": "1.0.0",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding",
                            "default": "utf-8"
                        }
                    },
                    "required": ["file_path"]
                },
                "is_active": True,
                "requires_auth": False,
                "rate_limit": 20
            },
            "calculator": {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "category": "utility",
                "version": "1.0.0",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                },
                "is_active": True,
                "requires_auth": False,
                "rate_limit": 50
            },
            "text_analysis": {
                "name": "text_analysis",
                "description": "Analyze text for sentiment, entities, and keywords",
                "category": "analysis",
                "version": "1.0.0",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis (sentiment, entities, keywords)",
                            "default": "sentiment"
                        }
                    },
                    "required": ["text"]
                },
                "is_active": True,
                "requires_auth": False,
                "rate_limit": 15
            },
            "code_execution": {
                "name": "code_execution",
                "description": "Execute code snippets safely",
                "category": "development",
                "version": "1.0.0",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to execute"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "default": "python"
                        }
                    },
                    "required": ["code"]
                },
                "is_active": True,
                "requires_auth": True,
                "rate_limit": 5
            },
            "image_analysis": {
                "name": "image_analysis",
                "description": "Analyze images for content and objects",
                "category": "vision",
                "version": "1.0.0",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the image to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis (objects, text, faces)",
                            "default": "objects"
                        }
                    },
                    "required": ["image_url"]
                },
                "is_active": True,
                "requires_auth": True,
                "rate_limit": 10
            }
        }

    def get_available_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available tools, optionally filtered by category."""
        tools = list(self.available_tools.values())

        if category:
            tools = [tool for tool in tools if tool["category"] == category]

        return tools

    def get_tool_categories(self) -> List[Dict[str, Any]]:
        """Get tool categories."""
        categories = {}
        for tool in self.available_tools.values():
            category = tool["category"]
            if category not in categories:
                categories[category] = {
                    "name": category,
                    "description": f"{category.capitalize()} tools",
                    "tool_count": 0,
                    "is_active": True
                }
            categories[category]["tool_count"] += 1

        return list(categories.values())

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        conversation_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        start_time = datetime.utcnow()

        # Check if tool exists
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool = self.available_tools[tool_name]

        # Check rate limit
        if not await self._check_rate_limit(tool_name, user_id):
            raise ValueError(f"Rate limit exceeded for tool '{tool_name}'")

        # Create tool execution record
        execution = ToolExecution(
            conversation_id=conversation_id,
            tool_name=tool_name,
            input_data=parameters,
            status="running"
        )
        self.db.add(execution)
        self.db.commit()

        try:
            # Execute the tool
            result = await self._execute_tool_function(tool_name, parameters)

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Update execution record
            execution.output_data = result
            execution.execution_time = int(execution_time * 1000)  # Convert to milliseconds
            execution.status = "completed"
            execution.updated_at = datetime.utcnow()
            self.db.commit()

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "tool_name": tool_name
            }

        except Exception as e:
            # Update execution record with error
            execution.status = "failed"
            execution.error_message = str(e)
            execution.updated_at = datetime.utcnow()
            self.db.commit()

            raise e

    async def _execute_tool_function(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute the actual tool function."""
        # Simulate tool execution - in real implementation, this would call actual tool APIs
        await asyncio.sleep(0.1)  # Simulate processing time

        if tool_name == "web_search":
            return {
                "results": [
                    {"title": "Result 1", "url": "https://example.com/1", "snippet": "Sample result 1"},
                    {"title": "Result 2", "url": "https://example.com/2", "snippet": "Sample result 2"}
                ],
                "query": parameters.get("query", ""),
                "num_results": len(parameters.get("results", []))
            }

        elif tool_name == "calculator":
            try:
                # Simple calculator - in real implementation, use proper expression evaluation
                expression = parameters.get("expression", "")
                # This is a very basic calculator - replace with proper expression evaluator
                result = eval(expression) if expression else 0
                return {"result": result, "expression": expression}
            except Exception as e:
                raise ValueError(f"Calculation error: {str(e)}")

        elif tool_name == "text_analysis":
            text = parameters.get("text", "")
            analysis_type = parameters.get("analysis_type", "sentiment")

            if analysis_type == "sentiment":
                return {
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "text_length": len(text),
                    "analysis_type": analysis_type
                }
            elif analysis_type == "entities":
                return {
                    "entities": ["entity1", "entity2"],
                    "text_length": len(text),
                    "analysis_type": analysis_type
                }
            else:
                return {
                    "keywords": ["keyword1", "keyword2"],
                    "text_length": len(text),
                    "analysis_type": analysis_type
                }

        elif tool_name == "file_read":
            # Simulate file reading
            return {
                "content": "Sample file content",
                "file_path": parameters.get("file_path", ""),
                "size": 1024,
                "encoding": parameters.get("encoding", "utf-8")
            }

        elif tool_name == "code_execution":
            # Simulate code execution
            code = parameters.get("code", "")
            language = parameters.get("language", "python")
            return {
                "output": f"Executed {language} code",
                "execution_time": 0.1,
                "success": True
            }

        elif tool_name == "image_analysis":
            # Simulate image analysis
            return {
                "objects": ["object1", "object2"],
                "confidence": 0.9,
                "image_url": parameters.get("image_url", ""),
                "analysis_type": parameters.get("analysis_type", "objects")
            }

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _check_rate_limit(self, tool_name: str, user_id: int) -> bool:
        """Check if user has exceeded rate limit for a tool."""
        tool = self.available_tools.get(tool_name, {})
        rate_limit = tool.get("rate_limit")

        if not rate_limit:
            return True

        # Use Redis to track rate limits
        key = f"rate_limit:{user_id}:{tool_name}"
        current_count = redis_manager.get(key) or 0

        if current_count >= rate_limit:
            return False

        # Increment counter with 1 minute expiration
        redis_manager.set(key, current_count + 1, ex=60)
        return True

    def get_execution_history(
        self,
        conversation_id: int,
        tool_name: Optional[str] = None,
        limit: int = 50
    ) -> List[ToolExecution]:
        """Get tool execution history."""
        query = self.db.query(ToolExecution).filter(
            ToolExecution.conversation_id == conversation_id
        )

        if tool_name:
            query = query.filter(ToolExecution.tool_name == tool_name)

        return query.order_by(ToolExecution.created_at.desc()).limit(limit).all()

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool."""
        tool = self.available_tools.get(tool_name)
        if tool:
            return {
                "description": tool["description"],
                "parameters": tool["parameters_schema"]
            }
        return None

    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool parameters."""
        errors = []
        warnings = []

        if tool_name not in self.available_tools:
            errors.append(f"Tool '{tool_name}' not found")
            return {"is_valid": False, "errors": errors, "warnings": warnings}

        tool = self.available_tools[tool_name]
        schema = tool["parameters_schema"]

        # Check required parameters
        required_params = schema.get("properties", {})
        required = schema.get("required", [])

        for param in required:
            if param not in parameters:
                errors.append(f"Required parameter '{param}' is missing")

        # Check parameter types
        for param, value in parameters.items():
            if param in required_params:
                expected_type = required_params[param].get("type")
                if expected_type and not isinstance(value, self._get_python_type(expected_type)):
                    errors.append(f"Parameter '{param}' must be of type {expected_type}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _get_python_type(self, json_type: str) -> type:
        """Convert JSON type to Python type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_mapping.get(json_type, object)

    def get_usage_stats(self, conversation_id: int) -> Dict[str, Any]:
        """Get tool usage statistics for a conversation."""
        executions = self.db.query(ToolExecution).filter(
            ToolExecution.conversation_id == conversation_id
        ).all()

        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == "completed"])
        failed_executions = len([e for e in executions if e.status == "failed"])

        # Calculate average execution time
        execution_times = [e.execution_time for e in executions if e.execution_time]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Get most used tools
        tool_usage = {}
        for execution in executions:
            tool_name = execution.tool_name
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        most_used_tools = [
            {"tool_name": tool, "count": count}
            for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
        ]

        # Get execution by category
        category_usage = {}
        for execution in executions:
            tool = self.available_tools.get(execution.tool_name, {})
            category = tool.get("category", "unknown")
            category_usage[category] = category_usage.get(category, 0) + 1

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "average_execution_time": avg_execution_time,
            "most_used_tools": most_used_tools,
            "execution_by_category": category_usage
        }

    def clear_history(self, conversation_id: int) -> bool:
        """Clear tool execution history for a conversation."""
        executions = self.db.query(ToolExecution).filter(
            ToolExecution.conversation_id == conversation_id
        ).all()

        for execution in executions:
            self.db.delete(execution)

        self.db.commit()
        return True

    def get_available_processing_types(self) -> List[str]:
        """Get available file processing types."""
        return [
            "text_extraction",
            "image_analysis",
            "document_parsing",
            "audio_transcription",
            "video_analysis",
            "data_analysis",
            "content_summarization",
            "sentiment_analysis",
            "entity_extraction"
        ]