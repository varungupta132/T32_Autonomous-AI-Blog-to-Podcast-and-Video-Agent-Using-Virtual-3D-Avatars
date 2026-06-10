from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Database
    database_url: str = "sqlite:///./podcasts.db"
    
    # Server
    backend_port: int = 8000
    
    # Storage
    output_dir: Path = Path("./outputs")
    temp_dir: Path = Path("./temp")
    
    # Security
    api_rate_limit: int = 10
    max_blog_length: int = 10000
    
    class Config:
        env_file = ".env"

settings = Settings()

# Create directories
settings.output_dir.mkdir(exist_ok=True)
settings.temp_dir.mkdir(exist_ok=True)
