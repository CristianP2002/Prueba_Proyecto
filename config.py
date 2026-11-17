import os
class Config:
    SECRET_KEY = os.environ.get("PARKIA_SECRET", "dev-only-change-this-key")
    DATABASE = os.path.join("instance", "parkia.db")
    HOURLY_RATE = 3000
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
