# app/config.py
import os

# Simple configuration without pydantic-settings for now
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/chatbotdb")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_lg")
INTENT_MODEL = os.getenv("INTENT_MODEL", "facebook/bart-large-mnli")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
