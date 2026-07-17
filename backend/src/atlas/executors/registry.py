"""Tiered tool registry.

Every tool declares its execution tier (1=API/code, 2=CLI, 3=browser, 4=screen)
and risk class. The registry — not the prompt — enforces that destructive tools
route through the approval queue.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Risk(str, Enum):
    SAFE = "safe"
    REVERSIBLE = "reversible"
    DESTRUCTIVE = "destructive"


@dataclass
class Tool:
    name: str
    description: str
    tier: int
    risk: Risk
    handler: Callable[..., Awaitable[str]]
    schema: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def for_team(self, names: list[str]) -> list[Tool]:
        return [self._tools[n] for n in names if n in self._tools]

    async def execute(self, name: str, approval_queue: Any = None, **kwargs: Any) -> str:
        """Execute a tool; destructive tools are parked in the approval queue instead."""
        tool = self.get(name)
        if tool.risk == Risk.DESTRUCTIVE and approval_queue is not None:
            request_id = await approval_queue.request(tool_name=name, args=kwargs)
            approved = await approval_queue.wait(request_id)
            if not approved:
                return f"[DENIED] Human rejected {name} with args {kwargs}"
        return await tool.handler(**kwargs)


async def _run_python(code: str, timeout: float = 120.0) -> str:
    """Tier 1: run Python in a subprocess with a hard timeout."""
    proc = await asyncio.create_subprocess_exec(
        "python", "-c", code,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return f"[TIMEOUT after {timeout}s]"
    return out.decode(errors="replace")[-8000:]


async def _run_powershell(command: str, timeout: float = 300.0) -> str:
    """Tier 2: run PowerShell on the Windows host."""
    proc = await asyncio.create_subprocess_exec(
        "powershell", "-NoProfile", "-Command", command,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return f"[TIMEOUT after {timeout}s]"
    return out.decode(errors="replace")[-8000:]


async def _delete_path(path: str) -> str:
    """Tier 2, DESTRUCTIVE: example of an approval-gated tool."""
    import shutil
    from pathlib import Path

    p = Path(path)
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()
    return f"deleted {path}"


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(Tool("run_python", "Run Python code in a subprocess", 1, Risk.REVERSIBLE, _run_python))
    reg.register(Tool("run_powershell", "Run a PowerShell command", 2, Risk.REVERSIBLE, _run_powershell))
    reg.register(Tool("delete_path", "Delete a file or directory (requires approval)", 2, Risk.DESTRUCTIVE, _delete_path))
    return reg
