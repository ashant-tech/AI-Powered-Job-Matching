from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Job Matching System"
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    upload_dir: str = "uploads/cvs"
    embedding_model: str = "all-MiniLM-L6-v2"
    cors_origins: list[str] = ["http://localhost:3000"]

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@example.com"
    sms_api_key: str = ""


settings = Settings()
