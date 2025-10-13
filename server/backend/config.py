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

    @property
    def postgres_dns(self):
        return (
            f"postgresql+psycopg2://{config.postgres_user}:"
            f"{config.postgres_password}@{config.postgres_host}:"
            f"{config.postgres_port}/{config.postgres_db}"
        )


config = Config()
