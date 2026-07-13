"""Lightweight in-memory store for future agent conversations."""

from __future__ import annotations

from typing import Any


class ConversationMemory:
    """Simple process-local memory store for agent workflow state."""

    def __init__(self) -> None:
        """Initialize empty message and key-value storage."""

        self.messages: list[dict[str, str]] = []
        self.values: dict[str, Any] = {}

    def add_message(self, role: str, content: str) -> None:
        """Append a conversation message to memory."""

        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        """Return stored conversation messages."""

        return list(self.messages)

    def set_value(self, key: str, value: Any) -> None:
        """Store a lightweight value by key."""

        self.values[key] = value

    def get_value(self, key: str, default: Any = None) -> Any:
        """Read a lightweight value by key."""

        return self.values.get(key, default)

    def clear(self) -> None:
        """Clear all stored memory."""

        self.messages.clear()
        self.values.clear()
