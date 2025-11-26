from sqlmodel import SQLModel, Field, create_engine, Session, Column, Integer, String
from typing import Optional

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

