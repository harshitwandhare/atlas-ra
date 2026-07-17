"""ATLAS CLI: `atlas serve`, `atlas goal "..."`."""

from __future__ import annotations

import typer
import uvicorn

app = typer.Typer(help="ATLAS — Autonomous Task & Lab Assistant System")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Start the API gateway + orchestrator."""
    uvicorn.run("atlas.api.main:app", host=host, port=port, reload=reload)


@app.command()
def version() -> None:
    from atlas import __version__

    typer.echo(f"ATLAS {__version__}")


if __name__ == "__main__":
    app()
