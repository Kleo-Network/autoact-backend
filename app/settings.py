# app/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
# Override the system environment variables with the variables from the `.env` file.
load_dotenv(override=True)


class Settings:
    PROJECT_NAME: str = "AutoAct Backend"
    DB_URL: str = os.getenv("DB_URL")
    DB_NAME: str = os.getenv("DB_NAME")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")


settings = Settings()
