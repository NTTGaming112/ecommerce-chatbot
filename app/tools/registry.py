"""Tool Registry - Central management for all tools."""
import logging
from typing import Dict, List, Optional
from app.tools.base import Tool, ToolResult, ToolError

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} (read_only={tool.is_read_only})")

    def execute(self, name: str, params: dict, agent: str = "", customer_id: str = "") -> ToolResult:
        if name not in self._tools:
            return ToolResult(success=False, error=ToolError(error_type="ToolNotFound", message=f"Tool {name} not found", code="TOOL_NOT_FOUND"))
        return self._tools[name](params, customer_id=customer_id, agent=agent)

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[dict]:
        return [{"name": t.name, "description": t.description, "allowed_agents": t.allowed_agents, "is_read_only": t.is_read_only, "requires_confirmation": t.requires_confirmation} for t in self._tools.values()]

tool_registry = ToolRegistry()
