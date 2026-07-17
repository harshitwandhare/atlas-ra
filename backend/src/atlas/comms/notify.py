"""Notifier adapters. Telegram first (pattern reused from job-sentinel)."""

from __future__ import annotations

import json
import urllib.request


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    async def notify(self, message: str) -> None:
        data = json.dumps({"chat_id": self._chat_id, "text": message[:4000]}).encode()
        req = urllib.request.Request(
            self._url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass  # notification failure must never break the pipeline
