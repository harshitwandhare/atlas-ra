"""CLI: every command, offline (urllib mocked)."""

from __future__ import annotations

import json
import urllib.error
from typing import Any

from typer.testing import CliRunner

from atlas.cli import app

runner = CliRunner()


class FakeResponse:
    def __init__(self, body: Any) -> None:
        self._body = json.dumps(body).encode()

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *exc: Any) -> None:
        return None


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.startswith("ATLAS ")


def test_goal_prints_task_id(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=0):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data)
        return FakeResponse({"task_id": "abc123def456"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = runner.invoke(app, ["goal", "Install StreamDiffusion"])

    assert result.exit_code == 0
    assert result.output.strip() == "abc123def456"
    assert captured["url"] == "http://localhost:8000/goals"
    assert captured["body"] == {"goal": "Install StreamDiffusion"}


def test_goal_custom_api_url(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=0):
        captured["url"] = req.full_url
        return FakeResponse({"task_id": "x"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = runner.invoke(app, ["goal", "hi", "--api", "http://10.0.0.5:9000"])

    assert result.exit_code == 0
    assert captured["url"] == "http://10.0.0.5:9000/goals"


def test_goal_server_unreachable_exits_nonzero(monkeypatch):
    def fake_urlopen(req, timeout=0):
        raise urllib.error.URLError("actively refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = runner.invoke(app, ["goal", "hi"])

    assert result.exit_code == 1
    assert "cannot reach ATLAS" in result.output


def test_tasks_table(monkeypatch):
    rows = [
        {"id": "aaa", "state": "done", "team": "systems", "goal": "short goal"},
        {"id": "bbb", "state": "running", "team": "research", "goal": "g" * 80},
    ]
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda req, timeout=0: FakeResponse(rows)
    )
    result = runner.invoke(app, ["tasks"])

    assert result.exit_code == 0
    assert "aaa" in result.output and "short goal" in result.output
    assert "..." in result.output  # long goal truncated


def test_tasks_empty(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda req, timeout=0: FakeResponse([])
    )
    result = runner.invoke(app, ["tasks"])
    assert result.exit_code == 0
    assert "no tasks" in result.output


def test_unknown_command():
    result = runner.invoke(app, ["frobnicate"])
    assert result.exit_code != 0
