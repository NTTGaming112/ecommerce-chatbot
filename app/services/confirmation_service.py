"""Confirmation Service - Manages pending write actions (cancel order, return request) requiring user confirmation."""
import re
from typing import Dict, Any, Optional

class ConfirmationService:
    def __init__(self):
        self._pending_actions: Dict[str, Dict[str, Any]] = {}

    def set_pending(self, session_id: str, action_type: str, payload: Dict[str, Any], prompt: str):
        self._pending_actions[session_id] = {
            "action_type": action_type,
            "payload": payload,
            "prompt": prompt,
        }

    def get_pending(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._pending_actions.get(session_id)

    def clear_pending(self, session_id: str):
        self._pending_actions.pop(session_id, None)

    @staticmethod
    def is_confirm(message: str) -> bool:
        msg = message.strip().lower()
        patterns = [
            r"^(co|co\s+nhe|dong\s+y|chac\s+chan|xac\s+nhan|yes|ok|okay|yup|dung\s+roi)$",
            r"\b(dong\s+y|xac\s+nhan|chac\s+chan)\b",
        ]
        return any(re.search(p, msg) for p in patterns)

    @staticmethod
    def is_reject(message: str) -> bool:
        msg = message.strip().lower()
        patterns = [
            r"^(khong|thoi|huy|dung|no|cancel|nevermind)$",
            r"\b(khong\s+can|dung\s+huy|thoi\s+khong)\b",
        ]
        return any(re.search(p, msg) for p in patterns)

confirmation_service = ConfirmationService()
