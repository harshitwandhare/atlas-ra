"""Email adapter protocol + IMAP reference implementation.

Adapter pattern (as in job-sentinel): the watcher depends only on this protocol,
so Gmail API / MCP connector / IMAP are interchangeable backends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str
    thread_id: str = ""


class EmailAdapter(Protocol):
    def fetch_unread_from(self, sender_filter: str) -> list[Email]: ...
    def create_draft(self, to: str, subject: str, body: str) -> str: ...
    def send(self, draft_id: str) -> None: ...


class ImapAdapter:
    """Reference adapter: read via IMAP, draft/send via SMTP. Credentials come from
    the OS keyring — never from the repo."""

    def __init__(self, host: str, user: str) -> None:
        self._host = host
        self._user = user
        self._drafts: dict[str, tuple[str, str, str]] = {}

    def _password(self) -> str:
        import keyring

        pw: str | None = keyring.get_password("atlas-email", self._user)
        if not pw:
            raise RuntimeError("Set the password: keyring set atlas-email <user>")
        return pw

    def fetch_unread_from(self, sender_filter: str) -> list[Email]:
        import email as email_lib
        import imaplib

        conn = imaplib.IMAP4_SSL(self._host)
        conn.login(self._user, self._password())
        conn.select("INBOX")
        _, data = conn.search(None, f'(UNSEEN FROM "{sender_filter}")')
        results = []
        ids = data[0] if isinstance(data[0], bytes) else b""
        for num in ids.split():
            _, msg_data = conn.fetch(num.decode(), "(RFC822)")
            raw = msg_data[0]
            if not isinstance(raw, tuple):
                continue
            msg = email_lib.message_from_bytes(raw[1])
            body = ""
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body = payload.decode(errors="replace")
                    break
            results.append(
                Email(
                    id=num.decode(),
                    sender=msg["From"] or "",
                    subject=msg["Subject"] or "",
                    body=body,
                )
            )
        conn.logout()
        return results

    def create_draft(self, to: str, subject: str, body: str) -> str:
        draft_id = f"draft-{len(self._drafts)}"
        self._drafts[draft_id] = (to, subject, body)
        return draft_id

    def send(self, draft_id: str) -> None:
        import smtplib
        from email.mime.text import MIMEText

        to, subject, body = self._drafts[draft_id]
        msg = MIMEText(body)
        msg["Subject"], msg["From"], msg["To"] = subject, self._user, to
        with smtplib.SMTP_SSL(self._host.replace("imap", "smtp")) as smtp:
            smtp.login(self._user, self._password())
            smtp.send_message(msg)
