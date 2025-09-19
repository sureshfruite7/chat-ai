import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GENAI_API_KEY = os.getenv("GENAI_API_KEY")
    GENAI_BASE_URL = os.getenv("GENAI_BASE_URL")
    GENAI_MODEL = os.getenv("GENAI_MODEL")
    VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

settings = Settings()