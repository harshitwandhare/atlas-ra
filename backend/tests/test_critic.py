import pytest

from atlas.teams.critic import Critic


@pytest.mark.asyncio
async def test_critic_rejects_empty_and_approves_clean():
    critic = Critic()
    assert not (await critic.review("goal", "")).approved
    assert (await critic.review("goal", "Setup complete. Smoke test passed.")).approved


@pytest.mark.asyncio
async def test_critic_rejects_transcript_ending_with_error():
    critic = Critic()
    # transcript tail contains "error" so the heuristic rejects
    verdict = await critic.review("goal", "Running step 1... step 2 crashed with error")
    assert not verdict.approved
    assert verdict.feedback


@pytest.mark.asyncio
async def test_critic_approves_when_error_only_in_early_section():
    """'error' appearing only before the last 500 chars should not trigger rejection."""
    critic = Critic()
    # put "error" well before the final 500-char window
    early = "Encountered an error early on but recovered."
    padding = "Step completed. " * 40  # 640 chars of clean text after the error
    verdict = await critic.review("goal", early + padding)
    assert verdict.approved


@pytest.mark.asyncio
async def test_critic_verdict_carries_summary_on_approval():
    critic = Critic()
    transcript = "x" * 2000 + "done"
    verdict = await critic.review("goal", transcript)
    assert verdict.approved
    assert verdict.summary  # non-empty summary distilled from the transcript
