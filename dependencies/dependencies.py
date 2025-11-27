from sqlmodel import Session, select
from db.database import engine
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Header
from models.models import User
from jose import jwt, JWTError
from core.config import settings
from models.models import Role
from sqlalchemy.orm import selectinload
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_session():
    with Session(engine) as session:
        yield session
        
async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = session.get(User, user_uuid)
    if not user or user is None:
        raise credentials_exception
    
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user does not have enough privileges")
    return current_user

async def validate_refresh_token(
    refresh_token: str = Header(..., alias="x-refresh-token"), 
    session: Session = Depends(get_session)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
    )

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("scope") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        user_uuid = uuid.UUID(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    statement = select(User).where(User.id == user_uuid).options(selectinload(User.private_data)) # type: ignore
    user = session.exec(statement).first()

    if not user or not user.private_data:
        raise credentials_exception

    if user.private_data.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")

    return user