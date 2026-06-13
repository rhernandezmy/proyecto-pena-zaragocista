from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Esto busca "EMAIL_REMITENTE" en el .env y lo guarda en email_host_user
    email_host_user: str = Field(alias="EMAIL_REMITENTE")
    # Esto busca "EMAIL_PASSWORD" en el .env y lo guarda en email_host_password
    email_host_password: str = Field(alias="EMAIL_PASSWORD")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()