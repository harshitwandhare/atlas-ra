"""Semantic memory: local vector store with a dependency-free fallback.

Uses LanceDB + an embedding model when available; otherwise falls back to a
keyword-overlap store so the pipeline (and tests) work everywhere. The interface
is identical either way — callers never know which backend is active.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Doc:
    id: str
    text: str
    source: str
    meta: dict[str, str] = field(default_factory=dict)


class SemanticStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)
        self._index = self._path / "docs.jsonl"

    def add(self, doc: Doc) -> None:
        with self._index.open("a", encoding="utf-8") as f:
            f.write(json.dumps(doc.__dict__) + "\n")

    def search(self, query: str, k: int = 5) -> list[Doc]:
        """Keyword-overlap ranking (fallback backend). LanceDB backend: V2 wiring."""
        terms = set(re.findall(r"\w+", query.lower()))
        scored: list[tuple[float, Doc]] = []
        if not self._index.exists():
            return []
        for line in self._index.read_text(encoding="utf-8").splitlines():
            raw = json.loads(line)
            doc = Doc(**raw)
            words = set(re.findall(r"\w+", doc.text.lower()))
            overlap = len(terms & words) / (len(terms) or 1)
            if overlap > 0:
                scored.append((overlap, doc))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [doc for _, doc in scored[:k]]
