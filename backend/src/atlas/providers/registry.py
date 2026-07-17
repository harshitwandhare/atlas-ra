"""Provider registry — select the runtime via config, add new ones here only."""

from __future__ import annotations

from atlas.providers.base import AgentProvider
from atlas.providers.claude import ClaudeProvider
from atlas.providers.langgraph import LangGraphProvider
from atlas.providers.ollama import OllamaProvider

_PROVIDERS: dict[str, type] = {
    "claude": ClaudeProvider,
    "langgraph": LangGraphProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str) -> AgentProvider:
    try:
        return _PROVIDERS[name]()  # type: ignore[no-any-return]
    except KeyError as exc:
        raise ValueError(f"Unknown provider '{name}'. Available: {list(_PROVIDERS)}") from exc
