from fastapi import Depends, FastAPI
from dependencies.dependencies import get_current_user
from models.models import User, UserRead
from routes.user_routes import user_router
from routes.project_routes import project_router
from routes.auth_routes import auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)
@app.get("/me", response_model=UserRead)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

app.include_router(user_router)
app.include_router(project_router)
app.include_router(auth_router)