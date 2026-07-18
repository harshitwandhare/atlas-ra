"""Provider adapters: registry lookup, Ollama HTTP paths, Claude SDK normalization."""

from __future__ import annotations

import json
import sys
import types
import urllib.error
from typing import Any

import pytest

from atlas.events import EventType
from atlas.providers import get_provider
from atlas.providers.claude import ClaudeProvider, _normalize
from atlas.providers.ollama import OllamaProvider

RUN_ARGS = {"task_id": "t1", "system_prompt": "sys", "goal": "g", "tools": [], "context": ""}


def test_registry_known_and_unknown():
    assert get_provider("ollama").name == "ollama"
    assert get_provider("claude").name == "claude"
    with pytest.raises(ValueError, match="Unknown provider 'nope'"):
        get_provider("nope")


class FakeResponse:
    def __init__(self, body: dict[str, Any]) -> None:
        self._body = json.dumps(body).encode()

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *exc: Any) -> None:
        return None


async def test_ollama_success(monkeypatch):
    captured: dict[str, Any] = {}

    def fake_urlopen(req, timeout=0):
        captured["body"] = json.loads(req.data)
        return FakeResponse({"response": "hello from llama"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    events = [e async for e in OllamaProvider().run(**RUN_ARGS)]

    assert [e.type for e in events] == [EventType.MESSAGE_DELTA, EventType.DONE]
    assert events[0].payload["text"] == "hello from llama"
    assert captured["body"]["system"] == "sys"


async def test_ollama_network_error_yields_error_event(monkeypatch):
    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    events = [e async for e in OllamaProvider().run(**RUN_ARGS)]

    assert events[-1].type == EventType.ERROR
    assert "connection refused" in events[-1].payload["error"]


def _fake_sdk(query_impl):
    """Install a stub claude_agent_sdk module; returns it for inspection."""
    mod = types.ModuleType("claude_agent_sdk")
    mod.query = query_impl
    mod.ClaudeAgentOptions = lambda **kw: types.SimpleNamespace(**kw)
    return mod


async def test_claude_sdk_exception_yields_error_event(monkeypatch):
    async def exploding_query(prompt, options):
        yield types.SimpleNamespace(content=[types.SimpleNamespace(text="partial", name=None)])
        raise RuntimeError("Claude Code returned an error result: success")

    monkeypatch.setitem(sys.modules, "claude_agent_sdk", _fake_sdk(exploding_query))
    events = [e async for e in ClaudeProvider().run(**RUN_ARGS)]

    assert events[0].type == EventType.MESSAGE_DELTA
    assert events[-1].type == EventType.ERROR
    assert "error result" in events[-1].payload["error"]
    assert EventType.DONE not in [e.type for e in events]


async def test_claude_success_stream_ends_with_done(monkeypatch):
    async def happy_query(prompt, options):
        yield types.SimpleNamespace(content=[types.SimpleNamespace(text="answer", name=None)])

    monkeypatch.setitem(sys.modules, "claude_agent_sdk", _fake_sdk(happy_query))
    events = [e async for e in ClaudeProvider().run(**RUN_ARGS)]

    assert [e.type for e in events] == [EventType.MESSAGE_DELTA, EventType.DONE]


def test_normalize_text_and_tool_blocks():
    text_block = types.SimpleNamespace(text="hi", name=None)
    tool_block = types.SimpleNamespace(text=None, name="run_python", input={"code": "1"})
    message = types.SimpleNamespace(content=[text_block, tool_block])

    events = _normalize("t1", message)

    assert [e.type for e in events] == [EventType.MESSAGE_DELTA, EventType.TOOL_CALL]
    assert events[1].payload == {"tool": "run_python", "input": {"code": "1"}}


def test_normalize_empty_message():
    assert _normalize("t1", types.SimpleNamespace(content=None)) == []
    assert _normalize("t1", types.SimpleNamespace()) == []
