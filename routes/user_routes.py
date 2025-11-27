from fastapi import APIRouter, HTTPException, Depends, status
from models.models import UserCreate, UserRead, User, UserUpdate, PrivateData
from dependencies.dependencies import get_session
from passlib.context import CryptContext
from typing import List
from dependencies.dependencies import get_admin_user
import uuid
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select 

user_router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_admin_user)])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@user_router.post("/", response_model=UserRead)
async def create_user(user_input: UserCreate, session: Session = Depends(get_session)):
    hashed_password = pwd_context.hash(user_input.password)
    
    statement = select(User).where(User.email == user_input.email)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    new_user = User(name=user_input.name,
                    email=user_input.email,
                    role=user_input.role)
    
    new_private_data = PrivateData(
        user_id=new_user.id,
        hashed_password=hashed_password,
    )
    
    session.add(new_user)
    session.add(new_private_data)
    session.commit()
    session.refresh(new_user)
    
    return new_user

@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@user_router.get("/", response_model=List[UserRead])
async def get_all_user(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_update: UserUpdate, user_id: uuid.UUID, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id).options(selectinload(User.private_data)) #type: ignore
    db_user = session.exec(statement=statement).first()
    
    if not db_user or not db_user.private_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    
    user_data = user_update.model_dump(exclude_unset=True)

    if "email" in user_data and user_data["email"] != db_user.email:
        statement = select(User).where(User.email == user_data["email"])
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    
    if "password" in user_data:
        raw_password = user_data.pop("password")
        
        if db_user.private_data:
            hashed_password = pwd_context.hash(raw_password)
            db_user.private_data.hashed_password = hashed_password
            session.add(db_user.private_data)
    
    db_user.sqlmodel_update(user_data)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

@user_router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(db_user)
    session.commit()
    
    return {"detail": "User deleted successfully"}

