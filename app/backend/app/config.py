from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./.env", env_file_encoding="utf-8", extra="ignore")
    
    database_url : str
    cookie_secure : bool = False
    session_heures : int = 8
    max_echecs : int = 5
    verrou_minutes : int = 15
    
settings = Settings()