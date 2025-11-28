from sqlmodel import Session, select
from db.database import engine
from passlib.context import CryptContext
from models.models import User, PrivateData, Role
import dotenv

dotenv.load_dotenv()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

ADMIN_EMAIL = "admin@localhost.com"
ADMIN_PASSWORD = "12345678"


def seed_admin():
    with Session(engine) as session:
        statement = select(User).where(User.email == ADMIN_EMAIL)
        existing = session.exec(statement).first() 
        
        if existing:
            return KeyError
        
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
    
    new_user = User(name="admin",
                    email=ADMIN_EMAIL,
                    role=Role.ADMIN)
    
    new_private_data = PrivateData(
        user_id=new_user.id,
        hashed_password=hashed_password,
    )
    
    session.add(new_user)
    session.add(new_private_data)
    session.commit()
    session.refresh(new_user)
    
    return new_user
if __name__ == "__main__":
    seed_admin()
