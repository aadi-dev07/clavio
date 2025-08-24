import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # Google API
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # GitHub
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN", None)
    github_repo_owner: Optional[str] = os.getenv("GITHUB_REPO_OWNER", None)
    github_repo_name: Optional[str] = os.getenv("GITHUB_REPO_NAME", None)
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Scheduling
    report_schedule_hours: int = int(os.getenv("REPORT_SCHEDULE_HOURS", "24"))
    
    class Config:
        env_file = ".env"

settings = Settings()
