import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

_raw_private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
# Handle both literal \n (from some .env files) and actual newlines
FIREBASE_PRIVATE_KEY = _raw_private_key.replace("\\n", "\n") if _raw_private_key else None

FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
CLOUD_TASKS_QUEUE_NAME = os.getenv("CLOUD_TASKS_QUEUE_NAME")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-for-dev")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
MAX_DAILY_AI_CALLS_PER_USER = int(os.getenv("MAX_DAILY_AI_CALLS_PER_USER", 15))
