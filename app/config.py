from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "TaxCase OCR & Case Library"
    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./taxcase.db"
    storage_dir: str = "./storage"
    access_token_expire_minutes: int = 480
    ocr_engine: str = "tesseract"
    max_upload_mb: int = 25
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
