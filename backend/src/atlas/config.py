"""Runtime configuration, loaded from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_", env_file=".env", extra="ignore")

    provider: str = "claude"
    db_path: str = "atlas.db"
    skills_dir: str = "../skills"
    max_retries: int = 2
    checkpoint_every_n_steps: int = 20


settings = Settings()
