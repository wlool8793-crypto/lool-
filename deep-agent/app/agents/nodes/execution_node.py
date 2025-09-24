import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from app.services.cache_service import cache_service
from app.services.rate_limiter import rate_limiter
from app.core.config import settings
from app.agents.execution_engine import execution_engine
from app.models import ToolExecution, AgentState
import logging

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionNode:
    """
    Advanced execution node for tool and task execution
    """

    def __init__(self):
        self.execution_history = {}
        self.active_executions = {}
        self.execution_limits = {
            "max_concurrent_executions": 10,
            "max_execution_time": 300,  # 5 minutes
            "max_retries": 3,
            "retry_delay": 1.0
        }

        # Tool registry
        self.tool_registry = {
            "web_search": {
                "handler": self._execute_web_search,
                "timeout": 30,
                "requires_auth": False,
                "rate_limit": "web_search"
            },
            "file_read": {
                "handler": self._execute_file_read,
                "timeout": 10,
                "requires_auth": False,
                "rate_limit": "file_operations"
            },
            "file_write": {
                "handler": self._execute_file_write,
                "timeout": 30,
                "requires_auth": False,
                "rate_limit": "file_operations"
            },
            "code_execution": {
                "handler": self._execute_code,
                "timeout": 60,
                "requires_auth": True,
                "rate_limit": "code_execution"
            },
            "api_call": {
                "handler": self._execute_api_call,
                "timeout": 45,
                "requires_auth": False,
                "rate_limit": "api_calls"
            },
            "database_query": {
                "handler": self._execute_database_query,
                "timeout": 30,
                "requires_auth": True,
                "rate_limit": "database_operations"
            },
            "email_send": {
                "handler": self._execute_email_send,
                "timeout": 60,
                "requires_auth": True,
                "rate_limit": "email_operations"
            },
            "system_command": {
                "handler": self._execute_system_command,
                "timeout": 120,
                "requires_auth": True,
                "rate_limit": "system_commands"
            }
        }

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process execution requests with advanced orchestration
        """
        try:
            execution_plan = state.get("execution_plan", {})
            context = state.get("context", {})
            conversation_id = state.get("conversation_id")

            # Validate execution plan
            if not execution_plan:
                return {
                    "status": "error",
                    "error": "No execution plan provided",
                    "execution_results": {}
                }

            # Check resource constraints
            resource_check = await self._check_resource_constraints(execution_plan)
            if not resource_check["allowed"]:
                return {
                    "status": "error",
                    "error": resource_check["error"],
                    "execution_results": {}
                }

            # Execute plan based on strategy
            execution_strategy = execution_plan.get("strategy", "sequential")

            if execution_strategy == "parallel":
                results = await self._execute_parallel_plan(execution_plan, context, conversation_id)
            elif execution_strategy == "sequential":
                results = await self._execute_sequential_plan(execution_plan, context, conversation_id)
            elif execution_strategy == "adaptive":
                results = await self._execute_adaptive_plan(execution_plan, context, conversation_id)
            else:
                results = await self._execute_sequential_plan(execution_plan, context, conversation_id)

            # Process results and generate summary
            execution_summary = await self._generate_execution_summary(results, execution_plan)

            return {
                "status": "success",
                "execution_results": results,
                "execution_summary": execution_summary,
                "execution_metadata": {
                    "strategy": execution_strategy,
                    "total_tasks": len(execution_plan.get("tasks", [])),
                    "completed_tasks": sum(1 for r in results.values() if r.get("status") == "completed"),
                    "failed_tasks": sum(1 for r in results.values() if r.get("status") == "failed"),
                    "execution_time": execution_summary.get("total_execution_time", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Execution processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_results": {},
                "execution_metadata": {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    async def _check_resource_constraints(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if execution plan can be executed with current resources
        """
        tasks = execution_plan.get("tasks", [])

        # Check concurrent execution limit
        if len(tasks) > self.execution_limits["max_concurrent_executions"]:
            return {
                "allowed": False,
                "error": f"Too many concurrent tasks ({len(tasks)}). Maximum allowed: {self.execution_limits['max_concurrent_executions']}"
            }

        # Check total estimated execution time
        total_estimated_time = sum(task.get("estimated_time", 30) for task in tasks)
        if total_estimated_time > self.execution_limits["max_execution_time"]:
            return {
                "allowed": False,
                "error": f"Total estimated execution time ({total_estimated_time}s) exceeds limit ({self.execution_limits['max_execution_time']}s)"
            }

        # Check rate limits for tools
        tool_counts = {}
        for task in tasks:
            tool_type = task.get("tool", "unknown")
            tool_counts[tool_type] = tool_counts.get(tool_type, 0) + 1

        for tool_type, count in tool_counts.items():
            if tool_type in self.tool_registry:
                rate_limit_key = self.tool_registry[tool_type]["rate_limit"]
                # Simplified rate limit check - in production, use actual rate limiter
                if count > 10:  # Arbitrary limit per tool type
                    return {
                        "allowed": False,
                        "error": f"Too many executions of tool type '{tool_type}' ({count}). Limit: 10"
                    }

        return {"allowed": True}

    async def _execute_parallel_plan(
        self,
        execution_plan: Dict[str, Any],
        context: Dict[str, Any],
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Execute tasks in parallel with proper orchestration
        """
        tasks = execution_plan.get("tasks", [])
        execution_tasks = []

        for task in tasks:
            execution_task = {
                "task_id": str(uuid.uuid4()),
                "func": self._execute_task,
                "args": (task, context, conversation_id),
                "priority": task.get("priority", "normal"),
                "metadata": {
                    "tool": task.get("tool"),
                    "conversation_id": conversation_id
                }
            }
            execution_tasks.append(execution_task)

        # Execute tasks in parallel
        try:
            results = await execution_engine.execute_parallel_tasks(
                tasks=execution_tasks,
                max_concurrent=min(len(tasks), self.execution_limits["max_concurrent_executions"]),
                timeout=self.execution_limits["max_execution_time"]
            )

            # Convert results to task_id indexed dict
            task_results = {}
            for i, result in enumerate(results):
                task_id = execution_tasks[i]["task_id"]
                task_results[task_id] = result

            return task_results

        except Exception as e:
            logger.error(f"Parallel execution error: {e}")
            # Fallback to sequential execution
            return await self._execute_sequential_plan(execution_plan, context, conversation_id)

    async def _execute_sequential_plan(
        self,
        execution_plan: Dict[str, Any],
        context: Dict[str, Any],
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Execute tasks sequentially with dependency management
        """
        tasks = execution_plan.get("tasks", [])
        results = {}

        for task in tasks:
            task_id = str(uuid.uuid4())

            # Check if task should be executed based on dependencies
            dependencies = task.get("dependencies", [])
            if dependencies:
                can_execute = await self._check_task_dependencies(dependencies, results)
                if not can_execute:
                    results[task_id] = {
                        "status": "skipped",
                        "error": "Dependencies not satisfied",
                        "task": task,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    continue

            # Execute task
            try:
                result = await self._execute_task(task, context, conversation_id)
                results[task_id] = result

                # Update context with task results
                if result.get("status") == "completed" and result.get("result"):
                    context.update(result["result"].get("context", {}))

            except Exception as e:
                results[task_id] = {
                    "status": "failed",
                    "error": str(e),
                    "task": task,
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Check if we should stop on error
                if task.get("stop_on_error", True):
                    break

        return results

    async def _execute_adaptive_plan(
        self,
        execution_plan: Dict[str, Any],
        context: Dict[str, Any],
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Execute tasks with adaptive strategy based on resource availability
        """
        tasks = execution_plan.get("tasks", [])
        results = {}

        # Group tasks by priority and dependencies
        task_groups = await self._group_tasks_by_priority(tasks)

        for group_name, group_tasks in task_groups.items():
            # Check if we can execute this group in parallel
            group_size = len(group_tasks)
            max_parallel = min(
                group_size,
                self.execution_limits["max_concurrent_executions"],
                self._get_available_execution_slots()
            )

            if max_parallel > 1 and await self._can_execute_parallel(group_tasks):
                # Execute group in parallel
                group_results = await self._execute_task_group_parallel(
                    group_tasks, context, conversation_id, max_parallel
                )
            else:
                # Execute group sequentially
                group_results = await self._execute_task_group_sequential(
                    group_tasks, context, conversation_id
                )

            results.update(group_results)

            # Check if we should continue based on results
            if not await self._should_continue_execution(group_results):
                break

        return results

    async def _execute_task(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any],
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Execute a single task with proper error handling and retries
        """
        task_id = str(uuid.uuid4())
        tool_type = task.get("tool")

        # Get tool configuration
        tool_config = self.tool_registry.get(tool_type)
        if not tool_config:
            return {
                "status": "failed",
                "error": f"Unknown tool type: {tool_type}",
                "task": task,
                "timestamp": datetime.utcnow().isoformat()
            }

        # Check rate limit
        if tool_config["rate_limit"]:
            rate_limit_result = await rate_limiter.check_rate_limit(
                rule_name=tool_config["rate_limit"],
                identifier=f"conversation:{conversation_id}",
                weight=1
            )
            if not rate_limit_result["allowed"]:
                return {
                    "status": "failed",
                    "error": f"Rate limit exceeded for {tool_type}",
                    "task": task,
                    "timestamp": datetime.utcnow().isoformat()
                }

        # Execute with retries
        max_retries = task.get("max_retries", self.execution_limits["max_retries"])
        retry_delay = task.get("retry_delay", self.execution_limits["retry_delay"])

        for attempt in range(max_retries + 1):
            try:
                # Record execution start
                execution_data = {
                    "task_id": task_id,
                    "tool": tool_type,
                    "status": "running",
                    "start_time": datetime.utcnow().isoformat(),
                    "attempt": attempt + 1,
                    "task": task
                }

                self.active_executions[task_id] = execution_data

                # Execute tool
                result = await asyncio.wait_for(
                    tool_config["handler"](task, context),
                    timeout=tool_config["timeout"]
                )

                # Record success
                execution_data.update({
                    "status": "completed",
                    "end_time": datetime.utcnow().isoformat(),
                    "result": result
                })

                return {
                    "status": "completed",
                    "result": result,
                    "task": task,
                    "execution_time": (
                        datetime.fromisoformat(execution_data["end_time"]) -
                        datetime.fromisoformat(execution_data["start_time"])
                    ).total_seconds(),
                    "attempts": attempt + 1,
                    "timestamp": datetime.utcnow().isoformat()
                }

            except asyncio.TimeoutError:
                error_msg = f"Task timeout after {tool_config['timeout']} seconds"
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    execution_data.update({
                        "status": "timeout",
                        "end_time": datetime.utcnow().isoformat(),
                        "error": error_msg
                    })
                    return {
                        "status": "timeout",
                        "error": error_msg,
                        "task": task,
                        "attempts": attempt + 1,
                        "timestamp": datetime.utcnow().isoformat()
                    }

            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    execution_data.update({
                        "status": "failed",
                        "end_time": datetime.utcnow().isoformat(),
                        "error": error_msg
                    })
                    return {
                        "status": "failed",
                        "error": error_msg,
                        "task": task,
                        "attempts": attempt + 1,
                        "timestamp": datetime.utcnow().isoformat()
                    }

            finally:
                # Clean up active execution
                self.active_executions.pop(task_id, None)
                self.execution_history[task_id] = execution_data

    async def _execute_web_search(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web search tool
        """
        query = task.get("parameters", {}).get("query", "")
        max_results = task.get("parameters", {}).get("max_results", 10)

        # Simulate web search - in production, use actual search API
        await asyncio.sleep(1)  # Simulate network delay

        return {
            "tool": "web_search",
            "query": query,
            "results": [
                {
                    "title": f"Search result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a search result snippet for query: {query}"
                }
                for i in range(min(max_results, 5))
            ],
            "total_results": min(max_results, 5),
            "context": {
                "web_search_performed": True,
                "search_query": query,
                "search_results_count": min(max_results, 5)
            }
        }

    async def _execute_file_read(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file read tool
        """
        file_path = task.get("parameters", {}).get("file_path", "")

        # Simulate file read - in production, use actual file operations
        await asyncio.sleep(0.5)

        return {
            "tool": "file_read",
            "file_path": file_path,
            "content": f"Content of file {file_path} (simulated)",
            "size": 1024,
            "context": {
                "file_read": True,
                "file_path": file_path
            }
        }

    async def _execute_file_write(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute file write tool
        """
        file_path = task.get("parameters", {}).get("file_path", "")
        content = task.get("parameters", {}).get("content", "")

        # Simulate file write - in production, use actual file operations
        await asyncio.sleep(0.5)

        return {
            "tool": "file_write",
            "file_path": file_path,
            "size": len(content),
            "context": {
                "file_written": True,
                "file_path": file_path,
                "content_size": len(content)
            }
        }

    async def _execute_code(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code tool
        """
        code = task.get("parameters", {}).get("code", "")
        language = task.get("parameters", {}).get("language", "python")

        # Simulate code execution - in production, use secure code execution environment
        await asyncio.sleep(2)

        return {
            "tool": "code_execution",
            "language": language,
            "output": f"Code execution output for {language} code (simulated)",
            "exit_code": 0,
            "context": {
                "code_executed": True,
                "language": language
            }
        }

    async def _execute_api_call(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute API call tool
        """
        url = task.get("parameters", {}).get("url", "")
        method = task.get("parameters", {}).get("method", "GET")

        # Simulate API call - in production, use actual HTTP client
        await asyncio.sleep(1)

        return {
            "tool": "api_call",
            "url": url,
            "method": method,
            "status_code": 200,
            "response": {"message": "API call successful (simulated)"},
            "context": {
                "api_call_made": True,
                "url": url,
                "method": method
            }
        }

    async def _execute_database_query(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database query tool
        """
        query = task.get("parameters", {}).get("query", "")
        query_type = task.get("parameters", {}).get("type", "SELECT")

        # Simulate database query - in production, use actual database connection
        await asyncio.sleep(0.5)

        return {
            "tool": "database_query",
            "query": query,
            "query_type": query_type,
            "rows_affected": 1 if query_type.upper() != "SELECT" else 0,
            "results": [{"id": 1, "data": "Sample result"}] if query_type.upper() == "SELECT" else [],
            "context": {
                "database_query_executed": True,
                "query_type": query_type
            }
        }

    async def _execute_email_send(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute email send tool
        """
        to_email = task.get("parameters", {}).get("to", "")
        subject = task.get("parameters", {}).get("subject", "")
        body = task.get("parameters", {}).get("body", "")

        # Simulate email send - in production, use actual email service
        await asyncio.sleep(2)

        return {
            "tool": "email_send",
            "to": to_email,
            "subject": subject,
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "context": {
                "email_sent": True,
                "to": to_email,
                "subject": subject
            }
        }

    async def _execute_system_command(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute system command tool
        """
        command = task.get("parameters", {}).get("command", "")

        # Simulate system command - in production, use secure command execution
        await asyncio.sleep(1)

        return {
            "tool": "system_command",
            "command": command,
            "exit_code": 0,
            "stdout": f"Command output: {command}",
            "stderr": "",
            "context": {
                "command_executed": True,
                "command": command
            }
        }

    async def _generate_execution_summary(self, results: Dict[str, Any], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive execution summary
        """
        total_tasks = len(results)
        completed_tasks = sum(1 for r in results.values() if r.get("status") == "completed")
        failed_tasks = sum(1 for r in results.values() if r.get("status") in ["failed", "timeout"])
        skipped_tasks = sum(1 for r in results.values() if r.get("status") == "skipped")

        # Calculate total execution time
        execution_times = [r.get("execution_time", 0) for r in results.values() if r.get("execution_time")]
        total_execution_time = sum(execution_times)
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Tool usage statistics
        tool_usage = {}
        for result in results.values():
            if "task" in result and "tool" in result["task"]:
                tool = result["task"]["tool"]
                tool_usage[tool] = tool_usage.get(tool, 0) + 1

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "skipped_tasks": skipped_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_execution_time": total_execution_time,
            "average_execution_time": avg_execution_time,
            "tool_usage": tool_usage,
            "strategy": execution_plan.get("strategy", "sequential"),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _group_tasks_by_priority(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group tasks by priority level
        """
        groups = {
            "high": [],
            "normal": [],
            "low": []
        }

        for task in tasks:
            priority = task.get("priority", "normal")
            if priority in groups:
                groups[priority].append(task)

        return groups

    async def _check_task_dependencies(self, dependencies: List[str], results: Dict[str, Any]) -> bool:
        """
        Check if task dependencies are satisfied
        """
        for dep in dependencies:
            # Find if dependency task completed successfully
            dep_satisfied = False
            for result in results.values():
                if result.get("task", {}).get("id") == dep and result.get("status") == "completed":
                    dep_satisfied = True
                    break

            if not dep_satisfied:
                return False

        return True

    async def _can_execute_parallel(self, tasks: List[Dict[str, Any]]) -> bool:
        """
        Check if tasks can be executed in parallel
        """
        # Check if any tasks have dependencies on each other
        for task in tasks:
            dependencies = task.get("dependencies", [])
            for dep in dependencies:
                # If dependency is in the same group, can't execute in parallel
                for other_task in tasks:
                    if other_task.get("id") == dep:
                        return False

        return True

    async def _execute_task_group_parallel(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any],
        conversation_id: int,
        max_parallel: int
    ) -> Dict[str, Any]:
        """
        Execute a group of tasks in parallel
        """
        execution_tasks = []

        for task in tasks:
            execution_task = {
                "task_id": str(uuid.uuid4()),
                "func": self._execute_task,
                "args": (task, context, conversation_id),
                "priority": task.get("priority", "normal"),
                "metadata": {
                    "tool": task.get("tool"),
                    "conversation_id": conversation_id
                }
            }
            execution_tasks.append(execution_task)

        results = await execution_engine.execute_parallel_tasks(
            tasks=execution_tasks,
            max_concurrent=max_parallel,
            timeout=self.execution_limits["max_execution_time"]
        )

        # Convert results to task_id indexed dict
        task_results = {}
        for i, result in enumerate(results):
            task_id = execution_tasks[i]["task_id"]
            task_results[task_id] = result

        return task_results

    async def _execute_task_group_sequential(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any],
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Execute a group of tasks sequentially
        """
        results = {}

        for task in tasks:
            task_id = str(uuid.uuid4())
            result = await self._execute_task(task, context, conversation_id)
            results[task_id] = result

            # Update context with task results
            if result.get("status") == "completed" and result.get("result"):
                context.update(result["result"].get("context", {}))

        return results

    def _get_available_execution_slots(self) -> int:
        """
        Get available execution slots
        """
        active_count = len(self.active_executions)
        return max(0, self.execution_limits["max_concurrent_executions"] - active_count)

    async def _should_continue_execution(self, results: Dict[str, Any]) -> bool:
        """
        Determine if execution should continue based on current results
        """
        # Stop if too many tasks failed
        failed_count = sum(1 for r in results.values() if r.get("status") in ["failed", "timeout"])
        total_count = len(results)

        if total_count > 0 and (failed_count / total_count) > 0.5:  # More than 50% failed
            return False

        return True

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific execution
        """
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]

        if execution_id in self.execution_history:
            return self.execution_history[execution_id]

        return None

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution
        """
        if execution_id in self.active_executions:
            self.active_executions[execution_id]["status"] = "cancelled"
            self.active_executions[execution_id]["end_time"] = datetime.utcnow().isoformat()
            return True

        return False

    async def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics
        """
        total_executions = len(self.execution_history)
        successful_executions = sum(
            1 for exec_data in self.execution_history.values()
            if exec_data.get("status") == "completed"
        )

        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0

        # Tool usage statistics
        tool_stats = {}
        for exec_data in self.execution_history.values():
            tool = exec_data.get("tool")
            if tool:
                tool_stats[tool] = tool_stats.get(tool, 0) + 1

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": success_rate,
            "active_executions": len(self.active_executions),
            "tool_usage": tool_stats,
            "execution_limits": self.execution_limits
        }


# Global instance
execution_node = ExecutionNode()