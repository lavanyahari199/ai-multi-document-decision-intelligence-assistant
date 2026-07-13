"""Memory tool skeleton for future agent workflows."""

from __future__ import annotations

from typing import Any


class MemoryTool:
    """Placeholder interface for future agent memory access."""

    def read(self, key: str) -> Any:
        """Read a value from agent memory."""

        # TODO: Connect to the conversation memory store in a future milestone.
        raise NotImplementedError("MemoryTool.read is not implemented yet.")

    def write(self, key: str, value: Any) -> None:
        """Write a value to agent memory."""

        # TODO: Connect to the conversation memory store in a future milestone.
        raise NotImplementedError("MemoryTool.write is not implemented yet.")
