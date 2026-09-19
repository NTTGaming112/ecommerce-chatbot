"""
Base Tool Classes
=================
Abstract base classes for all tools in the Multi-Agent system.

Tools are classified as:
  - ReadTool: Read-only, no side effects (e.g., get_order, search_products)
  - WriteTool: Can modify data, requires confirmation (e.g., create_refund, cancel_order)
"""
import uuid
import time
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal


@dataclass
class ToolResult:
    """Standard result returned by every tool execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional["ToolError"] = None
    latency_ms: float = 0.0
    cached: bool = False
    tool_name: str = ""
    tools_used: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error.to_dict() if self.error else None,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
            "tool_name": self.tool_name,
        }


@dataclass
class ToolError:
    """Structured error from tool execution."""
    error_type: str
    message: str
    code: str
    retryable: bool = False

    def to_dict(self) -> dict:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "code": self.code,
            "retryable": self.retryable,
        }


class Tool(ABC):
    """Abstract base class for all tools."""

    def __init__(
        self,
        name: str,
        description: str,
        allowed_agents: List[str],
        is_read_only: bool = True,
        requires_confirmation: bool = False,
    ):
        self.name = name
        self.description = description
        self.allowed_agents = allowed_agents
        self.is_read_only = is_read_only
        self.requires_confirmation = requires_confirmation

    def check_permission(self, agent: str) -> None:
        """Check if the given agent is allowed to use this tool."""
        if agent not in self.allowed_agents:
            raise PermissionError(
                f"Agent '{agent}' is not allowed to use tool '{self.name}'. "
                f"Allowed: {self.allowed_agents}"
            )

    def validate_access(self, params: Dict[str, Any], customer_id: str) -> None:
        """
        Validate data isolation — ensure the agent can only access
        data belonging to the requesting customer.
        Override in subclass for specific checks.
        """
        # Default: no extra validation
        pass

    def generate_idempotency_key(self, params: Dict[str, Any], customer_id: str) -> str:
        """Generate an idempotency key from tool name + params + customer."""
        raw = f"{self.name}:{customer_id}:{sorted(params.items())}"
        return hashlib.md5(raw.encode()).hexdigest()

    @abstractmethod
    def execute(self, params: Dict[str, Any], customer_id: str = "") -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def __call__(self, params: Dict[str, Any], customer_id: str = "", agent: str = "") -> ToolResult:
        """Convenience: check permission, validate, execute."""
        start = time.time()
        try:
            if agent:
                self.check_permission(agent)
            self.validate_access(params, customer_id)
            result = self.execute(params, customer_id)
            result.latency_ms = (time.time() - start) * 1000
            result.tool_name = self.name
            return result
        except PermissionError as e:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="PermissionDenied",
                    message=str(e),
                    code="PERMISSION_DENIED",
                    retryable=False,
                ),
                latency_ms=(time.time() - start) * 1000,
                tool_name=self.name,
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type=type(e).__name__,
                    message=str(e),
                    code=f"{self.name.upper()}_ERROR",
                    retryable=False,
                ),
                latency_ms=(time.time() - start) * 1000,
                tool_name=self.name,
            )


class ReadTool(Tool):
    """Base class for read-only tools (no side effects)."""

    def __init__(self, name: str, description: str, allowed_agents: List[str]):
        super().__init__(
            name=name,
            description=description,
            allowed_agents=allowed_agents,
            is_read_only=True,
            requires_confirmation=False,
        )


class WriteTool(Tool):
    """Base class for write/action tools (may modify data)."""

    def __init__(
        self,
        name: str,
        description: str,
        allowed_agents: List[str],
        requires_confirmation: bool = True,
    ):
        super().__init__(
            name=name,
            description=description,
            allowed_agents=allowed_agents,
            is_read_only=False,
            requires_confirmation=requires_confirmation,
        )
