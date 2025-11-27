from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from core.security import verify_password

from dependencies.dependencies import get_session, get_current_user
from models.models import User
from core.security import verify_password, create_access_token, create_refresh_token
from core.config import settings
from datetime import timedelta

from jose import jwt, JWTError
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> dict:    
    user = get_user_by_email(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Failed in Login. Verify Email and Password", 
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)},
                                       expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer"}


@auth_router.post("/refresh")
async def refresh_access_token(
    refresh_token: str = Header(...), # O token vem no Header ou Body (depende do front)
    session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("scope") != "refresh_token":
             raise HTTPException(status_code=401, detail="Invalid token scope")

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        user = session.get(User, int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")



def get_user_by_email(session: Session, email: str):
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()
