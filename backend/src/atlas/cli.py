"""ATLAS CLI: `atlas serve`, `atlas goal "..."`, `atlas tasks`, `atlas version`."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

import typer
import uvicorn

app = typer.Typer(help="ATLAS — Autonomous Task & Lab Assistant System")

DEFAULT_API = "http://localhost:8000"


def _request(url: str, data: dict[str, Any] | None = None) -> Any:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, OSError) as exc:
        typer.echo(f"error: cannot reach ATLAS at {url} ({exc}). Is `atlas serve` running?")
        raise typer.Exit(code=1) from exc


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Start the API gateway + orchestrator."""
    uvicorn.run("atlas.api.main:app", host=host, port=port, reload=reload)


@app.command()
def goal(text: str, api: str = DEFAULT_API) -> None:
    """Submit a goal to a running ATLAS server; prints the task id."""
    result = _request(f"{api}/goals", {"goal": text})
    typer.echo(result["task_id"])


@app.command()
def tasks(api: str = DEFAULT_API) -> None:
    """List all tasks in the ledger (id, state, team, goal)."""
    rows = _request(f"{api}/tasks")
    if not rows:
        typer.echo("no tasks")
        return
    for row in rows:
        goal_text = row["goal"] if len(row["goal"]) <= 60 else row["goal"][:57] + "..."
        typer.echo(f"{row['id']}  {row['state']:<10} {row['team']:<9} {goal_text}")


@app.command()
def version() -> None:
    from atlas import __version__

    typer.echo(f"ATLAS {__version__}")


if __name__ == "__main__":
    app()
