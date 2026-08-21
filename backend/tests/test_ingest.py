from unittest.mock import patch

from atlas.ingest.pipeline import fetch_video_transcript, ingest
from atlas.ingest.procedures import extract_procedure
from atlas.memory.semantic import SemanticStore


def test_text_ingest_and_search(tmp_path):
    src = tmp_path / "notes.md"
    src.write_text("Wan 2.2 needs the 5B model for 10GB VRAM budgets.", encoding="utf-8")
    store = SemanticStore(str(tmp_path / "sem"))
    ingest(str(src), store)
    hits = store.search("what model fits a 10GB VRAM budget?")
    assert hits and "5B" in hits[0].text


def test_procedure_extraction_from_tutorial():
    transcript = """
    welcome to the tutorial
    1. Install Python 3.10 from python.org
    2. Clone the StreamDiffusion repository
    3. Run pip install -e . inside the venv
    4. Open the examples folder and run main.py
    """
    draft = extract_procedure(transcript)
    assert draft and "DRAFT" in draft and "Clone the StreamDiffusion" in draft


def test_no_procedure_in_prose():
    assert extract_procedure("This is just an essay about art history.") is None


def test_fetch_video_transcript_guards_url_against_flag_injection(tmp_path):
    # A URL crafted to look like a yt-dlp flag must still be treated as the
    # video URL (not parsed as an option), and never reach a shell.
    hostile_url = "https://example.com/--exec=touch pwned"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        fetch_video_transcript(hostile_url, str(tmp_path))

    cmd = mock_run.call_args[0][0]
    assert cmd[-2:] == ["--", hostile_url]
    assert mock_run.call_args.kwargs.get("shell") is not True
