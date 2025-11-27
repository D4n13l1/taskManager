from dotenv import load_dotenv
import os
load_dotenv()
from passlib.context import CryptContext
from pydantic_settings import BaseSettings

try:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.environ["SECRET_KEY"]
except KeyError:
    raise KeyError("SECRET_KEY environment variable not set")
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 120)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 7)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class Settings(BaseSettings):
    SECRET_KEY: str = SECRET_KEY
    ALGORITHM: str = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS: int = REFRESH_TOKEN_EXPIRE_DAYS

settings = Settings()