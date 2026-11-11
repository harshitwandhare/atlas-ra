from email.message import EmailMessage
from unittest.mock import MagicMock

import pytest

from atlas.comms.email_adapter import ImapAdapter


def _raw(sender: str, subject: str, body: str) -> bytes:
    m = EmailMessage()
    m["From"], m["Subject"] = sender, subject
    m.set_content(body)
    return m.as_bytes()


@pytest.fixture
def adapter(monkeypatch):
    a = ImapAdapter("imap.example.com", "me@example.com")
    monkeypatch.setattr(a, "_password", lambda: "pw")
    return a


def _conn(monkeypatch, ids: bytes, raws: list[bytes]):
    conn = MagicMock()
    conn.search.return_value = ("OK", [ids])
    conn.fetch.side_effect = [("OK", [(b"1", raw)]) for raw in raws]
    monkeypatch.setattr("imaplib.IMAP4_SSL", lambda host: conn)
    return conn


def test_fetch_parses_messages_and_logs_out(adapter, monkeypatch):
    conn = _conn(monkeypatch, b"1 2", [_raw("a@x.edu", "Hi", "one"), _raw("b@x.edu", "Yo", "two")])
    out = adapter.fetch_unread_from("x.edu")
    assert [(e.id, e.sender, e.subject) for e in out] == [
        ("1", "a@x.edu", "Hi"),
        ("2", "b@x.edu", "Yo"),
    ]
    assert out[0].body.strip() == "one"
    conn.logout.assert_called_once()


def test_fetch_escapes_quotes_in_sender_filter(adapter, monkeypatch):
    conn = _conn(monkeypatch, b"", [])
    adapter.fetch_unread_from('x" OR ALL "')
    query = conn.search.call_args.args[1]
    assert query == '(UNSEEN FROM "x\\" OR ALL \\"")'


def test_fetch_logs_out_when_fetch_fails(adapter, monkeypatch):
    conn = _conn(monkeypatch, b"1", [])
    conn.fetch.side_effect = RuntimeError("boom")
    with pytest.raises(RuntimeError):
        adapter.fetch_unread_from("x.edu")
    conn.logout.assert_called_once()


def test_drafts_get_sequential_ids(adapter):
    assert adapter.create_draft("a@x.edu", "s", "b") == "draft-0"
    assert adapter.create_draft("a@x.edu", "s2", "b2") == "draft-1"


def test_send_uses_smtp_host_and_headers(adapter, monkeypatch):
    smtp = MagicMock()
    smtp.__enter__.return_value = smtp
    seen = {}

    def factory(host):
        seen["host"] = host
        return smtp

    monkeypatch.setattr("smtplib.SMTP_SSL", factory)
    d = adapter.create_draft("to@x.edu", "Subj", "Body")
    adapter.send(d)
    assert seen["host"] == "smtp.example.com"
    msg = smtp.send_message.call_args.args[0]
    assert (msg["To"], msg["From"], msg["Subject"]) == ("to@x.edu", "me@example.com", "Subj")


def test_password_missing_raises(monkeypatch):
    import sys
    import types

    fake = types.SimpleNamespace(get_password=lambda *a: None)
    monkeypatch.setitem(sys.modules, "keyring", fake)
    with pytest.raises(RuntimeError, match="keyring set"):
        ImapAdapter("imap.example.com", "me@example.com")._password()
