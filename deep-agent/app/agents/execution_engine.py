import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.cache_service import cache_service
from app.services.rate_limiter import rate_limiter
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    High-performance execution engine for agent operations
    """

    def __init__(self, max_workers: int = 10, timeout: int = 300):
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_executions = {}
        self.execution_history = {}

    async def execute_task(
        self,
        task_id: str,
        task_func: Callable,
        task_args: tuple = (),
        task_kwargs: Dict[str, Any] = None,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a single task with monitoring
        """
        task_kwargs = task_kwargs or {}
        execution_key = f"execution:{task_id}"

        try:
            # Record execution start
            execution_data = {
                "task_id": task_id,
                "status": "running",
                "start_time": datetime.utcnow().isoformat(),
                "priority": priority,
                "metadata": metadata or {},
                "progress": 0,
                "result": None,
                "error": None
            }

            self.active_executions[task_id] = execution_data
            await cache_service.set(execution_key, execution_data, ttl=self.timeout)

            # Execute task
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(*task_args, **task_kwargs)
            else:
                # Run in thread pool for blocking functions
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda: task_func(*task_args, **task_kwargs)
                )

            # Record success
            execution_data.update({
                "status": "completed",
                "end_time": datetime.utcnow().isoformat(),
                "result": result,
                "progress": 100
            })

        except Exception as e:
            # Record error
            execution_data.update({
                "status": "failed",
                "end_time": datetime.utcnow().isoformat(),
                "error": str(e),
                "progress": 0
            })
            logger.error(f"Task execution error for {task_id}: {e}")
            raise

        finally:
            # Cleanup and store result
            await cache_service.set(execution_key, execution_data, ttl=3600)
            self.execution_history[task_id] = execution_data
            self.active_executions.pop(task_id, None)

        return execution_data

    async def execute_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel
        """
        max_concurrent = max_concurrent or self.max_workers
        timeout = timeout or self.timeout
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_task(
                    task_id=task["task_id"],
                    task_func=task["func"],
                    task_args=task.get("args", ()),
                    task_kwargs=task.get("kwargs", {}),
                    priority=task.get("priority", "normal"),
                    metadata=task.get("metadata", {})
                )

        # Execute tasks with timeout
        tasks_with_timeout = asyncio.wait_for(
            asyncio.gather(*[execute_with_semaphore(task) for task in tasks]),
            timeout=timeout
        )

        try:
            return await tasks_with_timeout
        except asyncio.TimeoutError:
            logger.error("Parallel tasks execution timeout")
            raise

    async def execute_sequential_tasks(
        self,
        tasks: List[Dict[str, Any]],
        stop_on_error: bool = True,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute tasks sequentially with dependency management
        """
        timeout = timeout or self.timeout
        results = []

        for task in tasks:
            try:
                # Check timeout
                if (datetime.utcnow() - datetime.fromisoformat(task.get("start_time", datetime.utcnow().isoformat()))).total_seconds() > timeout:
                    raise TimeoutError("Sequential execution timeout")

                result = await self.execute_task(
                    task_id=task["task_id"],
                    task_func=task["func"],
                    task_args=task.get("args", ()),
                    task_kwargs=task.get("kwargs", {}),
                    priority=task.get("priority", "normal"),
                    metadata=task.get("metadata", {})
                )
                results.append(result)

                # Stop on error if configured
                if stop_on_error and result["status"] == "failed":
                    break

            except Exception as e:
                error_result = {
                    "task_id": task["task_id"],
                    "status": "failed",
                    "error": str(e),
                    "start_time": datetime.utcnow().isoformat(),
                    "end_time": datetime.utcnow().isoformat()
                }
                results.append(error_result)

                if stop_on_error:
                    break

        return results

    async def execute_workflow(
        self,
        workflow: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complex workflow with dependencies
        """
        workflow_id = workflow.get("id", str(uuid.uuid4()))
        execution_key = f"workflow:{workflow_id}"

        try:
            # Initialize workflow execution
            workflow_data = {
                "workflow_id": workflow_id,
                "status": "running",
                "start_time": datetime.utcnow().isoformat(),
                "context": context or {},
                "current_step": 0,
                "total_steps": len(workflow.get("steps", [])),
                "results": {},
                "errors": []
            }

            await cache_service.set(execution_key, workflow_data, ttl=self.timeout)

            # Execute workflow steps
            steps = workflow.get("steps", [])
            for i, step in enumerate(steps):
                step_id = step.get("id", f"step_{i}")
                workflow_data["current_step"] = i + 1

                try:
                    # Check dependencies
                    dependencies = step.get("dependencies", [])
                    if not await self._check_dependencies(dependencies, workflow_data["results"]):
                        raise ValueError(f"Dependencies not satisfied for step {step_id}")

                    # Execute step
                    step_result = await self._execute_workflow_step(step, workflow_data["context"])
                    workflow_data["results"][step_id] = step_result

                    # Update context with step results
                    if step.get("update_context", True):
                        workflow_data["context"].update(step_result.get("context", {}))

                    # Send progress update
                    workflow_data["progress"] = ((i + 1) / len(steps)) * 100
                    await cache_service.set(execution_key, workflow_data, ttl=self.timeout)

                except Exception as e:
                    workflow_data["errors"].append({
                        "step": step_id,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    if step.get("required", False):
                        workflow_data["status"] = "failed"
                        break

            # Mark workflow as completed
            workflow_data.update({
                "status": "completed" if not workflow_data["errors"] else "partial",
                "end_time": datetime.utcnow().isoformat(),
                "progress": 100
            })

        except Exception as e:
            workflow_data.update({
                "status": "failed",
                "end_time": datetime.utcnow().isoformat(),
                "errors": workflow_data["errors"] + [{
                    "step": "workflow",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }]
            })
            logger.error(f"Workflow execution error: {e}")

        finally:
            await cache_service.set(execution_key, workflow_data, ttl=3600)

        return workflow_data

    async def _execute_workflow_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step
        """
        step_type = step.get("type", "task")

        if step_type == "task":
            return await self.execute_task(
                task_id=step["id"],
                task_func=step["func"],
                task_args=step.get("args", ()),
                task_kwargs=step.get("kwargs", {}),
                priority=step.get("priority", "normal"),
                metadata=step.get("metadata", {})
            )

        elif step_type == "parallel":
            return await self.execute_parallel_tasks(
                tasks=step["tasks"],
                max_concurrent=step.get("max_concurrent"),
                timeout=step.get("timeout")
            )

        elif step_type == "sequential":
            return await self.execute_sequential_tasks(
                tasks=step["tasks"],
                stop_on_error=step.get("stop_on_error", True),
                timeout=step.get("timeout")
            )

        elif step_type == "condition":
            return await self._execute_condition_step(step, context)

        elif step_type == "loop":
            return await self._execute_loop_step(step, context)

        else:
            raise ValueError(f"Unknown step type: {step_type}")

    async def _execute_condition_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute conditional step
        """
        condition_func = step["condition"]
        condition_result = condition_func(context)

        if condition_result:
            if "then" in step:
                return await self._execute_workflow_step(step["then"], context)
        else:
            if "else" in step:
                return await self._execute_workflow_step(step["else"], context)

        return {"status": "completed", "result": None}

    async def _execute_loop_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute loop step
        """
        loop_type = step.get("loop_type", "for")
        max_iterations = step.get("max_iterations", 100)

        results = []

        if loop_type == "for":
            iterations = step.get("iterations", 1)
            for i in range(min(iterations, max_iterations)):
                loop_context = context.copy()
                loop_context["iteration"] = i
                result = await self._execute_workflow_step(step["body"], loop_context)
                results.append(result)

        elif loop_type == "while":
            condition_func = step["condition"]
            iteration = 0
            while condition_func(context) and iteration < max_iterations:
                loop_context = context.copy()
                loop_context["iteration"] = iteration
                result = await self._execute_workflow_step(step["body"], loop_context)
                results.append(result)
                iteration += 1

        return {"status": "completed", "results": results}

    async def _check_dependencies(
        self,
        dependencies: List[str],
        results: Dict[str, Any]
    ) -> bool:
        """
        Check if step dependencies are satisfied
        """
        for dep in dependencies:
            if dep not in results or results[dep]["status"] != "completed":
                return False
        return True

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution status
        """
        execution_data = await cache_service.get(f"execution:{execution_id}")
        if execution_data:
            return execution_data

        workflow_data = await cache_service.get(f"workflow:{execution_id}")
        return workflow_data

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution
        """
        if execution_id in self.active_executions:
            self.active_executions[execution_id]["status"] = "cancelled"
            self.active_executions[execution_id]["end_time"] = datetime.utcnow().isoformat()
            await cache_service.set(
                f"execution:{execution_id}",
                self.active_executions[execution_id],
                ttl=3600
            )
            return True
        return False

    async def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics
        """
        active_count = len(self.active_executions)
        total_executions = len(self.execution_history)

        # Calculate success rate
        successful_executions = sum(
            1 for exec_data in self.execution_history.values()
            if exec_data["status"] == "completed"
        )

        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0

        # Calculate average execution time
        execution_times = []
        for exec_data in self.execution_history.values():
            if exec_data.get("end_time") and exec_data.get("start_time"):
                start_time = datetime.fromisoformat(exec_data["start_time"])
                end_time = datetime.fromisoformat(exec_data["end_time"])
                execution_times.append((end_time - start_time).total_seconds())

        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        return {
            "active_executions": active_count,
            "total_executions": total_executions,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "max_workers": self.max_workers,
            "timeout": self.timeout
        }

    async def cleanup_old_executions(self, days: int = 7):
        """
        Clean up old execution data
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        cutoff_iso = cutoff_time.isoformat()

        cleaned_count = 0
        for exec_id, exec_data in list(self.execution_history.items()):
            if exec_data.get("start_time", "") < cutoff_iso:
                del self.execution_history[exec_id]
                cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} old execution records")
        return cleaned_count


class TaskScheduler:
    """
    Task scheduler for recurring and scheduled tasks
    """

    def __init__(self):
        self.scheduled_tasks = {}
        self.running = False

    async def schedule_task(
        self,
        task_id: str,
        task_func: Callable,
        schedule_type: str,
        schedule_value: Union[int, str],
        task_args: tuple = (),
        task_kwargs: Dict[str, Any] = None,
        start_time: Optional[datetime] = None
    ):
        """
        Schedule a recurring task
        """
        self.scheduled_tasks[task_id] = {
            "func": task_func,
            "args": task_args,
            "kwargs": task_kwargs or {},
            "schedule_type": schedule_type,
            "schedule_value": schedule_value,
            "start_time": start_time or datetime.utcnow(),
            "last_run": None,
            "next_run": self._calculate_next_run(schedule_type, schedule_value, start_time or datetime.utcnow())
        }

    def _calculate_next_run(
        self,
        schedule_type: str,
        schedule_value: Union[int, str],
        start_time: datetime
    ) -> datetime:
        """
        Calculate next run time for scheduled task
        """
        if schedule_type == "interval":
            return start_time + timedelta(seconds=schedule_value)
        elif schedule_type == "cron":
            # Simplified cron parsing - in production, use a proper cron library
            return start_time + timedelta(minutes=15)  # Default to 15 minutes
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")

    async def start_scheduler(self):
        """
        Start the task scheduler
        """
        self.running = True
        while self.running:
            try:
                await self._run_due_tasks()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

    async def stop_scheduler(self):
        """
        Stop the task scheduler
        """
        self.running = False

    async def _run_due_tasks(self):
        """
        Run tasks that are due
        """
        current_time = datetime.utcnow()

        for task_id, task_data in list(self.scheduled_tasks.items()):
            if current_time >= task_data["next_run"]:
                try:
                    # Execute task
                    if asyncio.iscoroutinefunction(task_data["func"]):
                        await task_data["func"](*task_data["args"], **task_data["kwargs"])
                    else:
                        task_data["func"](*task_data["args"], **task_data["kwargs"])

                    # Update schedule
                    task_data["last_run"] = current_time
                    task_data["next_run"] = self._calculate_next_run(
                        task_data["schedule_type"],
                        task_data["schedule_value"],
                        current_time
                    )

                except Exception as e:
                    logger.error(f"Scheduled task error for {task_id}: {e}")


# Global instances
execution_engine = ExecutionEngine()
task_scheduler = TaskScheduler()