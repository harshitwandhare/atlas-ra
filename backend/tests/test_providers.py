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
    mod.ClaudeAgentOptions = types.SimpleNamespace
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


class _Msg:
    def __init__(self, content: str) -> None:
        self.content = content


def _install_fake_langgraph(monkeypatch: pytest.MonkeyPatch, chunks: list[dict[str, Any]]):
    seen: dict[str, Any] = {}

    class FakeAgent:
        async def astream(self, payload: dict[str, Any], stream_mode: str):
            seen["payload"] = payload
            seen["stream_mode"] = stream_mode
            for chunk in chunks:
                yield chunk

    def init_chat_model(model: str) -> str:
        seen["model"] = model
        return model

    def create_react_agent(**kwargs: Any) -> FakeAgent:
        seen["agent_kwargs"] = kwargs
        return FakeAgent()

    chat = types.ModuleType("langchain.chat_models")
    chat.init_chat_model = init_chat_model  # type: ignore[attr-defined]
    prebuilt = types.ModuleType("langgraph.prebuilt")
    prebuilt.create_react_agent = create_react_agent  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "langchain", types.ModuleType("langchain"))
    monkeypatch.setitem(sys.modules, "langchain.chat_models", chat)
    monkeypatch.setitem(sys.modules, "langgraph", types.ModuleType("langgraph"))
    monkeypatch.setitem(sys.modules, "langgraph.prebuilt", prebuilt)
    return seen


async def test_langgraph_reports_missing_dependency(monkeypatch):
    from atlas.providers.langgraph import LangGraphProvider

    # A None entry in sys.modules makes the import raise ImportError.
    monkeypatch.setitem(sys.modules, "langgraph.prebuilt", None)
    events = [e async for e in LangGraphProvider().run(**RUN_ARGS)]
    assert [e.type for e in events] == [EventType.ERROR]
    assert "pip install langgraph" in events[0].payload["error"]


async def test_langgraph_streams_messages_and_skips_empty(monkeypatch):
    from atlas.providers.langgraph import LangGraphProvider

    chunks = [
        {"messages": [_Msg("")]},
        {"messages": [_Msg("hello")]},
        {"messages": [_Msg("hello world")]},
    ]
    seen = _install_fake_langgraph(monkeypatch, chunks)
    events = [e async for e in LangGraphProvider(model="x:y").run(**RUN_ARGS)]

    assert [e.type for e in events] == [
        EventType.MESSAGE_DELTA,
        EventType.MESSAGE_DELTA,
        EventType.DONE,
    ]
    assert [e.payload["text"] for e in events[:2]] == ["hello", "hello world"]
    assert seen["model"] == "x:y"
    assert seen["agent_kwargs"]["prompt"] == "sys"
    assert seen["payload"]["messages"] == [("user", "g")]


async def test_langgraph_prepends_context_to_goal(monkeypatch):
    from atlas.providers.langgraph import LangGraphProvider

    seen = _install_fake_langgraph(monkeypatch, [])
    args = {**RUN_ARGS, "context": "prior notes"}
    events = [e async for e in LangGraphProvider().run(**args)]

    assert [e.type for e in events] == [EventType.DONE]
    assert seen["payload"]["messages"] == [("user", "prior notes\n\n# Goal\ng")]
