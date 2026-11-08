from __future__ import annotations

from contextlib import contextmanager

import pytest

from atlas.observability import tracing


class _Span:
    def __init__(self) -> None:
        self.attrs: dict[str, str] = {}

    def set_attribute(self, key: str, value: str) -> None:
        self.attrs[key] = value


class _Tracer:
    def __init__(self) -> None:
        self.spans: list[tuple[str, _Span]] = []

    @contextmanager
    def start_as_current_span(self, name: str):
        span = _Span()
        self.spans.append((name, span))
        yield span


def test_traced_event_is_a_noop_without_a_tracer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tracing, "_tracer", None)
    ran = False
    with tracing.traced_event("plan", "t1", "planner"):
        ran = True
    assert ran


def test_traced_event_records_task_and_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    tracer = _Tracer()
    monkeypatch.setattr(tracing, "_tracer", tracer)
    with tracing.traced_event("plan", "t1", "planner"):
        pass
    assert len(tracer.spans) == 1
    name, span = tracer.spans[0]
    assert name == "plan"
    assert span.attrs == {"atlas.task_id": "t1", "atlas.agent": "planner"}


def test_traced_event_does_not_swallow_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tracing, "_tracer", _Tracer())
    with pytest.raises(ValueError):
        with tracing.traced_event("plan", "t1", "planner"):
            raise ValueError("boom")
