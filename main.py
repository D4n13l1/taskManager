from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from routes.user_routes import user_router
from routes.project_routes import project_router
load_dotenv()
try:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.environ["SECRET_KEY"]
except KeyError:
    raise KeyError("SECRET_KEY environment variable not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

app = FastAPI()


# pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app.include_router(user_router)
app.include_router(project_router)