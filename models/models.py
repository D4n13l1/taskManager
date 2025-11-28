from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy import Column, ForeignKey as SA_FK
from typing import Optional, List
from enum import Enum
import uuid
from pydantic import EmailStr


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    
class ProjectRole(str, Enum):
    MANAGER = "manager"
    VIEWER = "viewer"
    EDITOR = "editor"

class ProjectUserLink(SQLModel, table=True):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", primary_key=True)
    project_role: Optional[ProjectRole] = Field(default=ProjectRole.VIEWER)

class PrivateData(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id",primary_key=True)
    
    hashed_password: str
    refresh_token: Optional[str] = None

    user: "User" = Relationship(back_populates="private_data")
class UserBase(SQLModel):
    name: str
    email: EmailStr = Field(index=True, unique=True)
    role: Role = Role.USER

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    
class UserRead(UserBase):
    id: uuid.UUID

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    private_data: Optional[PrivateData] = Relationship(back_populates="user", 
                                                       sa_relationship_kwargs={
                                                           "uselist": False,
                                                           "cascade":"all, delete-orphan",
                                                       })

    # Projetos criados por este usuário (dono)
    created_projects: List["Project"] = Relationship(back_populates="owner")
    tasks_assigned: List["Task"] = Relationship(back_populates="assigned_to")

    # Projetos dos quais este usuário participa (many-to-many)
    participating_projects: List["Project"] = Relationship(back_populates="participants", link_model=ProjectUserLink)
    
    
class ProjectCreate(SQLModel):
    title: str
    manager_id: Optional[uuid.UUID] = None
    description: Optional[str] = ""
class ProjectRead(SQLModel):
    id: int
    title: str
    owner: UserRead
    description: str
    participants: List[UserRead] = Field(default_factory=list)

class ProjectReadOnCreate(SQLModel):
    id: int
    title: str
    owner: UserRead
    description: str

class ProjectReadTask(SQLModel):
    id: int
    title: str
    owner: UserRead
    
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(default="No description provided")
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")

    # Dono (criado por)
    owner: Optional[User] = Relationship(back_populates="created_projects")

    # Participantes (n-to-n)
    participants: List[User] = Relationship(back_populates="participating_projects", link_model=ProjectUserLink)
    
    #tasks 
    tasks: List["Task"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    
    
    
class StatusTask(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "inprogress"
    DONE = "done"

class UrgencyTask(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: StatusTask = StatusTask.TODO
    urgency: UrgencyTask = UrgencyTask.LOW
    
    project_id: Optional[int] = Field(default=None, sa_column=Column(SA_FK("project.id", ondelete="CASCADE"), nullable=True))
    assigned_to_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    
    assigned_to: Optional[User] = Relationship(back_populates="tasks_assigned")
    project: Optional[Project] = Relationship(back_populates="tasks")
    
class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    status: StatusTask = StatusTask.TODO
    urgency: UrgencyTask = UrgencyTask.LOW
    assigned_to_id: Optional[uuid.UUID] = None
    
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusTask] = None
    urgency: Optional[UrgencyTask] = None
    assigned_to_id: Optional[uuid.UUID] = None
    
class TaskReadOnCreate(SQLModel):
    id: int
    title: str
    description: str
    status: StatusTask
    urgency: UrgencyTask
    project_id: int
    assigned_to: UserRead
    
class TaskRead(SQLModel):
    id: int
    title: str
    description: str
    status: StatusTask
    urgency: UrgencyTask
    project: ProjectReadTask
    assigned_to: UserRead
    
    
class Login(SQLModel):
    email: str
    password: str