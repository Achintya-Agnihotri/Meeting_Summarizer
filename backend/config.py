from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    whisper_model: str = "base"
    whisper_model_dir: Path = Path("local_models/whisper")
    whisper_cpu_threads: int = 4
    whisper_num_workers: int = 2
    ollama_model: str = "llama3.2:1b"
    ollama_base_url: str = "http://127.0.0.1:11434"
    max_upload_size_mb: int = 25
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
