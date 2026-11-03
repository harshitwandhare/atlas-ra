import json
from unittest.mock import patch

import pytest

from atlas.comms.notify import TelegramNotifier


@pytest.mark.asyncio
async def test_notify_posts_json_to_the_bot_endpoint():
    with patch("atlas.comms.notify.urllib.request.urlopen") as urlopen:
        await TelegramNotifier("TOKEN", "42").notify("hello")

    req = urlopen.call_args.args[0]
    assert req.full_url == "https://api.telegram.org/botTOKEN/sendMessage"
    assert req.get_header("Content-type") == "application/json"
    assert json.loads(req.data) == {"chat_id": "42", "text": "hello"}


@pytest.mark.asyncio
async def test_notify_truncates_long_messages():
    with patch("atlas.comms.notify.urllib.request.urlopen") as urlopen:
        await TelegramNotifier("TOKEN", "42").notify("x" * 5000)

    sent = json.loads(urlopen.call_args.args[0].data)
    assert len(sent["text"]) == 4000


@pytest.mark.asyncio
async def test_notify_swallows_network_errors():
    with patch("atlas.comms.notify.urllib.request.urlopen", side_effect=OSError("down")):
        await TelegramNotifier("TOKEN", "42").notify("hello")
