"""Shared ConversationState for the Multi-Agent system."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Message:
    role: str  # "customer" | "assistant" | "system"
    content: str
    timestamp: str = ""
    agent_id: str = ""


@dataclass
class TaskExecution:
    task_name: str = ""
    agent: str = ""
    status: str = "pending"  # pending|running|completed|failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ConversationState:
    # Identity
    conversation_id: str = ""
    customer_id: str = ""
    session_id: str = ""
    trace_id: str = ""

    # Conversation
    messages: List[Message] = field(default_factory=list)
    current_message: str = ""

    # Router Output
    intent: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    urgency: str = "medium"
    sentiment: float = 0.0

    # Task Execution
    task_plan: List[Dict[str, Any]] = field(default_factory=list)
    current_task: str = ""
    completed_tasks: List[TaskExecution] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)

    # Agent Results
    agent_results: Dict[str, Any] = field(default_factory=dict)

    # Errors
    errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    # Confirmations
    pending_confirmations: List[Dict[str, Any]] = field(default_factory=list)

    # Handoff
    handoff: Optional[Dict[str, Any]] = None

    # Output
    final_response: str = ""
    actions_taken: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def __post_init__(self):
        if not self.conversation_id:
            self.conversation_id = str(uuid.uuid4())
        if not self.trace_id:
            self.trace_id = str(uuid.uuid4())
