from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from core.security import verify_password
from sqlalchemy.orm import selectinload

from dependencies.dependencies import get_session, get_current_user
from models.models import User
from core.security import verify_password, create_access_token, create_refresh_token
from core.config import settings
from datetime import timedelta
from dependencies.dependencies import validate_refresh_token

from jose import jwt, JWTError
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> dict:    
    statement = (select(User).where(User.email == form_data.username)
                 .options(selectinload(User.private_data))) #type: ignore
    user = session.exec(statement=statement).first()
    
    if not user or not user.private_data or not verify_password(form_data.password, user.private_data.hashed_password): 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Failed in Login. Verify Email and Password", 
                            headers={"WWW-Authenticate": "Bearer"},
                            )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)},
                                       expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    user.private_data.refresh_token = refresh_token
    session.add(user.private_data)
    session.commit()
    
    return {"access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer"}

@auth_router.post("/refresh")
async def refresh_token(user: User = Depends(validate_refresh_token), session: Session = Depends(get_session)):
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    if user.private_data:
        user.private_data.refresh_token = new_refresh_token
        session.add(user.private_data)
        session.commit()
    
    return { 
        "access_token": access_token, 
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }