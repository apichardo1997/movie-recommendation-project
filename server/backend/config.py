from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Config for local dev environment

    Automatically read modifications to the configuration parameters
    from ``.env`` file.
    """

    postgres_user: str = Field(min_length=1)
    postgres_password: str = Field(min_length=1)
    postgres_db: str = Field(min_length=1)
    postgres_host: str = Field(min_length=1)
    postgres_port: int = Field()
    postgres_exposed_port: int | None = Field(None)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8",
    )


config = Config()
