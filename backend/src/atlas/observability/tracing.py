"""OpenTelemetry span per agent event. No-op if the SDK isn't configured,
so tracing never becomes a hard dependency of correctness."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

_tracer: Any = None
try:
    from opentelemetry import trace

    _tracer = trace.get_tracer("atlas")
except ImportError:  # pragma: no cover
    pass


@contextmanager
def traced_event(name: str, task_id: str, agent: str) -> Iterator[None]:
    if _tracer is None:
        yield
        return
    with _tracer.start_as_current_span(name) as span:
        span.set_attribute("atlas.task_id", task_id)
        span.set_attribute("atlas.agent", agent)
        yield
