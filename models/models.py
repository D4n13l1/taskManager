from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy import Column, ForeignKey as SA_FK
from typing import Optional, List
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ProjectUserLink(SQLModel, table=True):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)


class UserBase(SQLModel):
    name: str
    email: str
    role: Role = Role.USER

class UserCreate(UserBase):
    password: str
    
class UserRead(UserBase):
    id: int

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str

    # Projetos criados por este usuário (dono)
    created_projects: List["Project"] = Relationship(back_populates="owner")
    tasks_assigned: List["Task"] = Relationship(back_populates="assigned_to")

    # Projetos dos quais este usuário participa (many-to-many)
    participating_projects: List["Project"] = Relationship(back_populates="participants", link_model=ProjectUserLink)
class ProjectCreate(SQLModel):
    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    
    
class ProjectRead(SQLModel):
    id: int
    title: str
    owner: UserRead
    participants: List[UserRead] = Field(default_factory=list)
    
class ProjectReadTask(SQLModel):
    id: int
    title: str
    owner: UserRead
    
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Dono (criado por)
    owner: Optional[User] = Relationship(back_populates="created_projects")

    # Participantes (many-to-many)
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
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    assigned_to: Optional[User] = Relationship(back_populates="tasks_assigned")
    project: Optional[Project] = Relationship(back_populates="tasks")
    
class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None
    status: StatusTask = StatusTask.TODO
    urgency: UrgencyTask = UrgencyTask.LOW
    assigned_to_id: Optional[int] = None
    
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
    