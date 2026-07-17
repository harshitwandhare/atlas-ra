import pytest

from atlas.teams.critic import Critic


@pytest.mark.asyncio
async def test_critic_rejects_empty_and_approves_clean():
    critic = Critic()
    assert not (await critic.review("goal", "")).approved
    assert (await critic.review("goal", "Setup complete. Smoke test passed.")).approved
