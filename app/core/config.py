from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DRIVER_NAME: str

    @property
    def database_url(self) -> str:
        return (
             f"{self.DRIVER_NAME}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    # DATABASE_URL = postgresql+pscopg2://usuario:password@localhost:5432/test_db

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()