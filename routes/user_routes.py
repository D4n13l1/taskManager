from fastapi import APIRouter, HTTPException, Depends, status
from models.models import UserCreate, UserRead, User, UserUpdate
from dependencies.dependencies import get_session
from passlib.context import CryptContext
from typing import List
from routes.auth_routes import get_user_by_email
from dependencies.dependencies import get_current_user
from models.models import Role

from sqlmodel import Session, select 

user_router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@user_router.post("/", response_model=UserRead)
async def create_user(user_input: UserCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User can not create User")
    print("CurrentUser", current_user)
    hashed_password = pwd_context.hash(user_input.password)
    statement = select(User).where(User.email == user_input.email)
    if session.exec(statement).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    db_user = User(name=user_input.name, email=user_input.email, password=hashed_password, role=user_input.role)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.get("/", response_model=List[UserRead])
async def get_all_user(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_update: UserUpdate, user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        hashed_password = pwd_context.hash(user_data["password"])
        user_data["password"] = hashed_password
    
    if "email" in user_data and user_data["email"] != db_user.email:
            existing_user = get_user_by_email(session, user_data["email"])
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already exists")

    db_user.sqlmodel_update(user_data)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@user_router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)
    session.commit()
    
    return {"detail": "User deleted successfully"}

