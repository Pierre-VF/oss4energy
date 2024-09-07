import pydantic_settings
from dotenv import load_dotenv


class Settings(pydantic_settings.BaseSettings):
    GITHUB_API_TOKEN: str

    model_config = pydantic_settings.SettingsConfigDict(
        env_file_encoding="utf-8",
    )


# Loading settings
load_dotenv(override=True)

SETTINGS = Settings()
