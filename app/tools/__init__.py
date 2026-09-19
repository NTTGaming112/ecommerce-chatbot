"""Tool Layer for Multi-Agent Customer Support"""
from app.tools.base import Tool, ReadTool, WriteTool, ToolResult, ToolError
from app.tools.registry import ToolRegistry, tool_registry

_initialized = False

def init_tools():
    global _initialized
    if _initialized: return
    from app.tools.read_tools import register_all_read_tools
    from app.tools.write_tools import register_all_write_tools
    register_all_read_tools(tool_registry)
    register_all_write_tools(tool_registry)
    _initialized = True

# Auto-init on import
init_tools()

__all__ = ["Tool", "ReadTool", "WriteTool", "ToolResult", "ToolError", "ToolRegistry", "tool_registry", "init_tools"]
