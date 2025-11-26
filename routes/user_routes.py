from fastapi import APIRouter, HTTPException, Depends
from models.models import UserCreate, UserRead, User, UserUpdate
from dependencies import get_session
from passlib.context import CryptContext
from typing import List

from sqlmodel import Session, select 

user_router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@user_router.post("/", response_model=UserRead)
async def create_user(user_input: UserCreate, session: Session = Depends(get_session)):
    hashed_password = pwd_context.hash(user_input.password)
    statement = select(User).where(User.email == user_input.email)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
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

def get_user_by_email(session: Session, email: str):
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()
