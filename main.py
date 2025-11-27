from fastapi import FastAPI
from routes.user_routes import user_router
from routes.project_routes import project_router
from routes.auth_routes import auth_router

app = FastAPI()

app.include_router(user_router)
app.include_router(project_router)
app.include_router(auth_router)