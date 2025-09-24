import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from app.services.cache_service import cache_service
from app.core.config import settings
from app.models import Message, AgentState
import logging

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    CODE = "code"
    LIST = "list"
    TABLE = "table"
    CHART = "chart"
    FILE = "file"


class OutputPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class OutputChannel(Enum):
    CHAT = "chat"
    NOTIFICATION = "notification"
    EMAIL = "email"
    WEBHOOK = "webhook"
    FILE = "file"
    API = "api"


@dataclass
class OutputContent:
    """Output content data structure"""
    id: str
    type: OutputFormat
    content: Union[str, Dict[str, Any]]
    priority: OutputPriority
    channel: OutputChannel
    created_at: datetime
    metadata: Dict[str, Any]
    ttl: Optional[int] = None
    recipient: Optional[str] = None
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None


class OutputNode:
    """
    Advanced output synthesis and delivery node
    """

    def __init__(self):
        self.output_templates = {
            "success": {
                "text": "✅ Task completed successfully!",
                "detailed": "✅ {task_name} completed successfully. {results_summary}"
            },
            "error": {
                "text": "❌ An error occurred",
                "detailed": "❌ Error in {task_name}: {error_message}"
            },
            "partial": {
                "text": "⚠️ Task partially completed",
                "detailed": "⚠️ {task_name} partially completed. {completed_count}/{total_count} tasks successful."
            },
            "progress": {
                "text": "🔄 Processing...",
                "detailed": "🔄 {task_name} in progress. {progress}% complete."
            },
            "information": {
                "text": "ℹ️ Information",
                "detailed": "ℹ️ {information_summary}"
            }
        }

        self.output_channels = {
            OutputChannel.CHAT: self._deliver_chat_output,
            OutputChannel.NOTIFICATION: self._deliver_notification_output,
            OutputChannel.EMAIL: self._deliver_email_output,
            OutputChannel.WEBHOOK: self._deliver_webhook_output,
            OutputChannel.FILE: self._deliver_file_output,
            OutputChannel.API: self._deliver_api_output
        }

        self.output_formatters = {
            OutputFormat.TEXT: self._format_text_output,
            OutputFormat.MARKDOWN: self._format_markdown_output,
            OutputFormat.HTML: self._format_html_output,
            OutputFormat.JSON: self._format_json_output,
            OutputFormat.CODE: self._format_code_output,
            OutputFormat.LIST: self._format_list_output,
            OutputFormat.TABLE: self._format_table_output,
            OutputFormat.CHART: self._format_chart_output,
            OutputFormat.FILE: self._format_file_output
        }

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and synthesize output from agent execution
        """
        try:
            conversation_id = state.get("conversation_id")
            user_id = state.get("user_id")
            execution_results = state.get("execution_results", {})
            execution_summary = state.get("execution_summary", {})
            enhanced_context = state.get("enhanced_context", {})
            processed_input = state.get("processed_data", {})

            # Analyze execution results to determine output strategy
            output_strategy = await self._determine_output_strategy(
                execution_results, execution_summary, processed_input
            )

            # Generate output content
            output_content = await self._generate_output_content(
                output_strategy, execution_results, execution_summary, enhanced_context
            )

            # Format output for different channels
            formatted_outputs = await self._format_output_content(output_content)

            # Deliver output through appropriate channels
            delivery_results = await self._deliver_output(formatted_outputs, conversation_id, user_id)

            # Store output history
            await self._store_output_history(output_content, delivery_results, conversation_id, user_id)

            # Generate response for user
            user_response = await self._generate_user_response(output_content, formatted_outputs)

            return {
                "status": "success",
                "output_content": output_content,
                "formatted_outputs": formatted_outputs,
                "delivery_results": delivery_results,
                "user_response": user_response,
                "output_metadata": {
                    "strategy": output_strategy,
                    "total_outputs": len(formatted_outputs),
                    "successful_deliveries": sum(1 for r in delivery_results.values() if r.get("success")),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Output processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_content": None,
                "formatted_outputs": {},
                "delivery_results": {},
                "user_response": "I apologize, but I encountered an error while processing the output. Please try again.",
                "output_metadata": {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    async def _determine_output_strategy(
        self,
        execution_results: Dict[str, Any],
        execution_summary: Dict[str, Any],
        processed_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine optimal output strategy based on execution results
        """
        strategy = {
            "primary_format": OutputFormat.MARKDOWN,
            "primary_channel": OutputChannel.CHAT,
            "output_level": "detailed",
            "include_visualizations": False,
            "include_attachments": False,
            "response_style": "conversational"
        }

        # Analyze execution results
        total_tasks = execution_summary.get("total_tasks", 0)
        completed_tasks = execution_summary.get("completed_tasks", 0)
        failed_tasks = execution_summary.get("failed_tasks", 0)
        success_rate = execution_summary.get("success_rate", 0)

        # Adjust strategy based on execution results
        if failed_tasks == 0 and completed_tasks > 0:
            # All successful
            strategy["output_level"] = "success"
            strategy["response_style"] = "celebratory"
        elif failed_tasks > 0:
            # Some failures
            strategy["output_level"] = "error" if success_rate < 50 else "partial"
            strategy["response_style"] = "apologetic"
        elif total_tasks == 0:
            # No tasks executed
            strategy["output_level"] = "information"
            strategy["response_style"] = "informational"

        # Check for data that needs special formatting
        tool_usage = execution_summary.get("tool_usage", {})
        if "database_query" in tool_usage or "web_search" in tool_usage:
            strategy["primary_format"] = OutputFormat.TABLE
            strategy["include_visualizations"] = True

        if "file_write" in tool_usage or "file_read" in tool_usage:
            strategy["include_attachments"] = True

        # Check input complexity
        input_complexity = processed_input.get("complexity_assessment", {}).get("complexity_score", 0)
        if input_complexity > 0.7:
            strategy["output_level"] = "detailed"
            strategy["include_visualizations"] = True

        return strategy

    async def _generate_output_content(
        self,
        output_strategy: Dict[str, Any],
        execution_results: Dict[str, Any],
        execution_summary: Dict[str, Any],
        enhanced_context: Dict[str, Any]
    ) -> OutputContent:
        """
        Generate comprehensive output content
        """
        output_id = str(uuid.uuid4())
        output_level = output_strategy["output_level"]

        # Generate base content
        base_content = await self._generate_base_content(
            output_level, execution_results, execution_summary
        )

        # Generate detailed sections
        detailed_sections = await self._generate_detailed_sections(
            execution_results, execution_summary, enhanced_context
        )

        # Generate summary
        summary = await self._generate_summary(execution_summary, detailed_sections)

        # Generate metadata
        metadata = await self._generate_output_metadata(
            output_strategy, execution_results, execution_summary
        )

        # Combine all content
        combined_content = {
            "base": base_content,
            "sections": detailed_sections,
            "summary": summary,
            "enhancements": enhanced_context.get("memory_enhancements", []),
            "timestamp": datetime.utcnow().isoformat()
        }

        return OutputContent(
            id=output_id,
            type=output_strategy["primary_format"],
            content=combined_content,
            priority=self._determine_priority(output_level),
            channel=output_strategy["primary_channel"],
            created_at=datetime.utcnow(),
            metadata=metadata,
            ttl=3600,  # 1 hour TTL
            conversation_id=enhanced_context.get("conversation_id"),
            user_id=enhanced_context.get("user_id")
        )

    async def _generate_base_content(
        self,
        output_level: str,
        execution_results: Dict[str, Any],
        execution_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate base output content
        """
        template = self.output_templates.get(output_level, self.output_templates["information"])

        if output_level == "success":
            return {
                "message": template["text"],
                "details": template["detailed"].format(
                    task_name="Task execution",
                    results_summary=self._format_results_summary(execution_summary)
                )
            }
        elif output_level == "error":
            failed_result = next(
                (r for r in execution_results.values() if r.get("status") == "failed"),
                {}
            )
            return {
                "message": template["text"],
                "details": template["detailed"].format(
                    task_name="Task execution",
                    error_message=failed_result.get("error", "Unknown error")
                )
            }
        elif output_level == "partial":
            return {
                "message": template["text"],
                "details": template["detailed"].format(
                    task_name="Task execution",
                    completed_count=execution_summary.get("completed_tasks", 0),
                    total_count=execution_summary.get("total_tasks", 0)
                )
            }
        else:
            return {
                "message": template["text"],
                "details": template["detailed"].format(
                    information_summary="Processing completed"
                )
            }

    async def _generate_detailed_sections(
        self,
        execution_results: Dict[str, Any],
        execution_summary: Dict[str, Any],
        enhanced_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed output sections
        """
        sections = []

        # Execution summary section
        sections.append({
            "title": "Execution Summary",
            "content": execution_summary,
            "type": "summary"
        })

        # Task results section
        if execution_results:
            successful_tasks = {k: v for k, v in execution_results.items() if v.get("status") == "completed"}
            failed_tasks = {k: v for k, v in execution_results.items() if v.get("status") == "failed"}

            if successful_tasks:
                sections.append({
                    "title": "Successful Tasks",
                    "content": successful_tasks,
                    "type": "success"
                })

            if failed_tasks:
                sections.append({
                    "title": "Failed Tasks",
                    "content": failed_tasks,
                    "type": "error"
                })

        # Tool usage section
        tool_usage = execution_summary.get("tool_usage", {})
        if tool_usage:
            sections.append({
                "title": "Tool Usage",
                "content": tool_usage,
                "type": "usage"
            })

        # Memory enhancements section
        memory_enhancements = enhanced_context.get("memory_enhancements", [])
        if memory_enhancements:
            sections.append({
                "title": "Memory Enhancements",
                "content": memory_enhancements,
                "type": "memory"
            })

        return sections

    async def _generate_summary(
        self,
        execution_summary: Dict[str, Any],
        detailed_sections: List[Dict[str, Any]]
    ) -> str:
        """
        Generate output summary
        """
        total_tasks = execution_summary.get("total_tasks", 0)
        completed_tasks = execution_summary.get("completed_tasks", 0)
        failed_tasks = execution_summary.get("failed_tasks", 0)
        success_rate = execution_summary.get("success_rate", 0)

        if total_tasks == 0:
            return "No tasks were executed."

        if success_rate == 100:
            return f"All {total_tasks} tasks completed successfully."
        elif success_rate > 0:
            return f"{completed_tasks} out of {total_tasks} tasks completed successfully ({success_rate:.1f}% success rate)."
        else:
            return f"All {total_tasks} tasks failed to complete."

    async def _generate_output_metadata(
        self,
        output_strategy: Dict[str, Any],
        execution_results: Dict[str, Any],
        execution_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate output metadata
        """
        return {
            "strategy": output_strategy,
            "execution_stats": execution_summary,
            "generated_at": datetime.utcnow().isoformat(),
            "content_hash": await self._generate_content_hash(execution_results),
            "estimated_reading_time": await self._estimate_reading_time(execution_results),
            "complexity_score": await self._calculate_complexity_score(execution_summary)
        }

    async def _format_output_content(self, output_content: OutputContent) -> Dict[OutputFormat, str]:
        """
        Format output content for different formats
        """
        formatted_outputs = {}

        # Format based on primary type and additional formats
        formats_to_generate = [
            output_content.type,
            OutputFormat.TEXT,  # Always generate text fallback
        ]

        # Add additional formats based on content
        if "table" in str(output_content.content).lower():
            formats_to_generate.append(OutputFormat.TABLE)
        if "list" in str(output_content.content).lower():
            formats_to_generate.append(OutputFormat.LIST)

        for output_format in set(formats_to_generate):
            if output_format in self.output_formatters:
                try:
                    formatted_content = await self.output_formatters[output_format](output_content)
                    formatted_outputs[output_format] = formatted_content
                except Exception as e:
                    logger.error(f"Error formatting output as {output_format}: {e}")
                    # Fallback to text
                    formatted_outputs[output_format] = await self.output_formatters[OutputFormat.TEXT](output_content)

        return formatted_outputs

    async def _deliver_output(
        self,
        formatted_outputs: Dict[OutputFormat, str],
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Deliver output through appropriate channels
        """
        delivery_results = {}

        # Deliver through primary channel
        for output_format, content in formatted_outputs.items():
            channel = self._determine_delivery_channel(output_format)
            if channel in self.output_channels:
                try:
                    result = await self.output_channels[channel](content, conversation_id, user_id)
                    delivery_results[f"{channel.value}_{output_format.value}"] = result
                except Exception as e:
                    logger.error(f"Error delivering output through {channel}: {e}")
                    delivery_results[f"{channel.value}_{output_format.value}"] = {
                        "success": False,
                        "error": str(e)
                    }

        return delivery_results

    async def _deliver_chat_output(
        self,
        content: str,
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Deliver output through chat channel
        """
        # Store in cache for WebSocket delivery
        cache_key = f"chat_output:{conversation_id}:{uuid.uuid4().hex[:8]}"
        await cache_service.set(cache_key, {
            "content": content,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "delivered": False
        }, ttl=3600)

        return {
            "success": True,
            "channel": "chat",
            "cache_key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _deliver_notification_output(
        self,
        content: str,
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Deliver output through notification channel
        """
        # Store in cache for notification system
        cache_key = f"notification:{user_id}:{uuid.uuid4().hex[:8]}"
        await cache_service.set(cache_key, {
            "content": content,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "agent_output"
        }, ttl=86400)  # 24 hours

        return {
            "success": True,
            "channel": "notification",
            "cache_key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _deliver_email_output(
        self,
        content: str,
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Deliver output through email channel
        """
        # Store in cache for email system
        cache_key = f"email_output:{user_id}:{uuid.uuid4().hex[:8]}"
        await cache_service.set(cache_key, {
            "content": content,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }, ttl=86400)  # 24 hours

        return {
            "success": True,
            "channel": "email",
            "cache_key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _deliver_webhook_output(
        self,
        content: str,
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Deliver output through webhook channel
        """
        # Store in cache for webhook delivery
        cache_key = f"webhook_output:{conversation_id}:{uuid.uuid4().hex[:8]}"
        await cache_service.set(cache_key, {
            "content": content,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }, ttl=3600)

        return {
            "success": True,
            "channel": "webhook",
            "cache_key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _deliver_file_output(
        self,
        content: str,
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Deliver output through file channel
        """
        # Store in cache for file generation
        cache_key = f"file_output:{conversation_id}:{uuid.uuid4().hex[:8]}"
        await cache_service.set(cache_key, {
            "content": content,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }, ttl=86400)  # 24 hours

        return {
            "success": True,
            "channel": "file",
            "cache_key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _deliver_api_output(
        self,
        content: str,
        conversation_id: Optional[int],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Deliver output through API channel
        """
        return {
            "success": True,
            "channel": "api",
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _store_output_history(
        self,
        output_content: OutputContent,
        delivery_results: Dict[str, Dict[str, Any]],
        conversation_id: Optional[int],
        user_id: Optional[int]
    ):
        """
        Store output in history
        """
        history_key = f"output_history:{conversation_id}:{output_content.id}"
        history_data = {
            "output_content": {
                "id": output_content.id,
                "type": output_content.type.value,
                "priority": output_content.priority.value,
                "channel": output_content.channel.value,
                "created_at": output_content.created_at.isoformat(),
                "metadata": output_content.metadata
            },
            "delivery_results": delivery_results,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        await cache_service.set(history_key, history_data, ttl=86400 * 7)  # 7 days

    async def _generate_user_response(
        self,
        output_content: OutputContent,
        formatted_outputs: Dict[OutputFormat, str]
    ) -> str:
        """
        Generate user-friendly response
        """
        # Use the most appropriate format for user response
        preferred_formats = [OutputFormat.MARKDOWN, OutputFormat.TEXT, OutputFormat.HTML]

        for format_type in preferred_formats:
            if format_type in formatted_outputs:
                content = formatted_outputs[format_type]

                # Extract base message if available
                if isinstance(output_content.content, dict) and "base" in output_content.content:
                    base_content = output_content.content["base"]
                    if "message" in base_content:
                        return f"{base_content['message']}\n\n{content}"

                return content

        # Fallback response
        return "I've processed your request and completed the necessary tasks."

    # Formatting methods
    async def _format_text_output(self, output_content: OutputContent) -> str:
        """Format output as plain text"""
        content = output_content.content
        if isinstance(content, dict):
            return json.dumps(content, indent=2)
        return str(content)

    async def _format_markdown_output(self, output_content: OutputContent) -> str:
        """Format output as Markdown"""
        content = output_content.content
        if not isinstance(content, dict):
            return str(content)

        markdown_lines = []

        # Add base content
        if "base" in content:
            base = content["base"]
            if "message" in base:
                markdown_lines.append(f"# {base['message']}")
            if "details" in base:
                markdown_lines.append(base['details'])
            markdown_lines.append("")

        # Add sections
        if "sections" in content:
            for section in content["sections"]:
                markdown_lines.append(f"## {section['title']}")
                markdown_lines.append(f"```json\n{json.dumps(section['content'], indent=2)}\n```")
                markdown_lines.append("")

        # Add summary
        if "summary" in content:
            markdown_lines.append("## Summary")
            markdown_lines.append(content["summary"])

        return "\n".join(markdown_lines)

    async def _format_html_output(self, output_content: OutputContent) -> str:
        """Format output as HTML"""
        content = output_content.content
        if not isinstance(content, dict):
            return f"<div>{str(content)}</div>"

        html_parts = []

        # Add base content
        if "base" in content:
            base = content["base"]
            if "message" in base:
                html_parts.append(f"<h1>{base['message']}</h1>")
            if "details" in base:
                html_parts.append(f"<p>{base['details']}</p>")

        # Add sections
        if "sections" in content:
            html_parts.append("<div class='sections'>")
            for section in content["sections"]:
                html_parts.append(f"<h2>{section['title']}</h2>")
                html_parts.append(f"<pre>{json.dumps(section['content'], indent=2)}</pre>")
            html_parts.append("</div>")

        return "".join(html_parts)

    async def _format_json_output(self, output_content: OutputContent) -> str:
        """Format output as JSON"""
        return json.dumps(output_content.content, indent=2)

    async def _format_code_output(self, output_content: OutputContent) -> str:
        """Format output as code block"""
        content = output_content.content
        return f"```\n{json.dumps(content, indent=2)}\n```"

    async def _format_list_output(self, output_content: OutputContent) -> str:
        """Format output as list"""
        content = output_content.content
        if not isinstance(content, dict):
            return f"- {str(content)}"

        list_items = []
        if "base" in content:
            list_items.append(f"- {content['base'].get('message', '')}")

        if "sections" in content:
            for section in content["sections"]:
                list_items.append(f"- {section['title']}: {len(section.get('content', {}))} items")

        return "\n".join(list_items)

    async def _format_table_output(self, output_content: OutputContent) -> str:
        """Format output as table"""
        content = output_content.content
        if not isinstance(content, dict):
            return f"| Content |\n|---------|\n| {str(content)} |"

        table_rows = ["| Section | Items |", "|----------|-------|"]

        if "sections" in content:
            for section in content["sections"]:
                item_count = len(section.get("content", {}))
                table_rows.append(f"| {section['title']} | {item_count} |")

        return "\n".join(table_rows)

    async def _format_chart_output(self, output_content: OutputContent) -> str:
        """Format output as chart (simplified)"""
        # Return chart data structure
        content = output_content.content
        return json.dumps({
            "type": "chart",
            "data": content,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _format_file_output(self, output_content: OutputContent) -> str:
        """Format output as file"""
        # Return file data structure
        content = output_content.content
        return json.dumps({
            "type": "file",
            "content": content,
            "filename": f"output_{output_content.id}.json",
            "timestamp": datetime.utcnow().isoformat()
        })

    # Helper methods
    def _determine_priority(self, output_level: str) -> OutputPriority:
        """Determine output priority based on level"""
        priority_map = {
            "success": OutputPriority.NORMAL,
            "error": OutputPriority.HIGH,
            "partial": OutputPriority.NORMAL,
            "information": OutputPriority.LOW
        }
        return priority_map.get(output_level, OutputPriority.NORMAL)

    def _determine_delivery_channel(self, output_format: OutputFormat) -> OutputChannel:
        """Determine delivery channel based on format"""
        channel_map = {
            OutputFormat.TEXT: OutputChannel.CHAT,
            OutputFormat.MARKDOWN: OutputChannel.CHAT,
            OutputFormat.HTML: OutputChannel.CHAT,
            OutputFormat.JSON: OutputChannel.API,
            OutputFormat.CODE: OutputChannel.CHAT,
            OutputFormat.LIST: OutputChannel.CHAT,
            OutputFormat.TABLE: OutputChannel.CHAT,
            OutputFormat.CHART: OutputChannel.CHAT,
            OutputFormat.FILE: OutputChannel.FILE
        }
        return channel_map.get(output_format, OutputChannel.CHAT)

    def _format_results_summary(self, execution_summary: Dict[str, Any]) -> str:
        """Format execution results summary"""
        total_tasks = execution_summary.get("total_tasks", 0)
        completed_tasks = execution_summary.get("completed_tasks", 0)
        failed_tasks = execution_summary.get("failed_tasks", 0)
        execution_time = execution_summary.get("total_execution_time", 0)

        parts = []
        if total_tasks > 0:
            parts.append(f"{completed_tasks}/{total_tasks} tasks completed")
        if execution_time > 0:
            parts.append(f"took {execution_time:.2f} seconds")

        return ", ".join(parts) if parts else "No tasks executed"

    async def _generate_content_hash(self, content: Dict[str, Any]) -> str:
        """Generate hash of content for deduplication"""
        import hashlib
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()

    async def _estimate_reading_time(self, content: Dict[str, Any]) -> int:
        """Estimate reading time in seconds"""
        content_str = json.dumps(content)
        word_count = len(content_str.split())
        # Average reading speed: 200 words per minute
        return max(1, int(word_count / 200 * 60))

    async def _calculate_complexity_score(self, execution_summary: Dict[str, Any]) -> float:
        """Calculate complexity score of output"""
        total_tasks = execution_summary.get("total_tasks", 0)
        tool_types = len(execution_summary.get("tool_usage", {}))
        failed_tasks = execution_summary.get("failed_tasks", 0)

        # Complexity based on number of tasks, tool diversity, and failure rate
        complexity = (total_tasks * 0.1) + (tool_types * 0.2) + (failed_tasks * 0.3)
        return min(1.0, complexity)


# Global instance
output_node = OutputNode()