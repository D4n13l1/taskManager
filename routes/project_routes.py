from fastapi import APIRouter, HTTPException, Depends, status
from models.models import ProjectCreate, Project, ProjectRead, TaskRead, User, Task, TaskCreate, TaskReadOnCreate, TaskUpdate, ProjectUserLink, ProjectRole, ProjectReadOnCreate, Role
from dependencies.dependencies import get_session, get_current_user
from typing import List

from sqlmodel import Session, select , or_, and_
from sqlalchemy.exc import IntegrityError

project_router = APIRouter(prefix="/projects", tags=["projects and tasks"], dependencies=[Depends(get_current_user)])

@project_router.post("/", response_model=ProjectReadOnCreate)
async def create_project(project_data: ProjectCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_project = Project(title=project_data.title, description=project_data.description, owner_id=current_user.id)
    session.add(db_project)
    print(f"id Enviado: {project_data.manager_id}")
    
    session.flush() # Cria o id mas sem commit ainda
    session.refresh(db_project)
    
    if project_data.manager_id and project_data.manager_id != current_user.id:
        db_manager = session.get(User, project_data.manager_id)
        if not db_manager:
            session.rollback() # Cancela criação se user não existir
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
        print(f"id Resgatado do banco: {db_manager}")
        print(f"Manager: {db_manager}")
        manager_link = ProjectUserLink(project_id=db_project.id, user_id=db_manager.id, project_role=ProjectRole.MANAGER)
        session.add(manager_link)
        
        owner_link = ProjectUserLink(project_id=db_project.id, user_id=current_user.id, project_role=ProjectRole.EDITOR)
        session.add(owner_link)
    else:
        owner_link = ProjectUserLink(
            project_id=db_project.id, 
            user_id=current_user.id, 
            project_role=ProjectRole.MANAGER
        )
        session.add(owner_link)
        
    session.commit()
    
    return db_project

@project_router.post("/add_user", response_model=Project)
async def add_user_to_project(user_id: int, project_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    db_project = session.get(Project, project_id)
    if not db_user or not db_project:
        raise HTTPException(status_code=404, detail="User or project not found")

    if db_user in db_project.participants:
        return db_project

    db_project.participants.append(db_user)
    try:
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already added to project")
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not add user to project")

    return db_project
    
@project_router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):   
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.role == Role.ADMIN:
        return db_project
    if db_project.owner_id == current_user.id:
        return db_project
    
    statement = select(ProjectUserLink).where(
        ProjectUserLink.project_id == project_id,
        ProjectUserLink.user_id == current_user.id
    )
    is_member = session.exec(statement=statement).first()
    if is_member:
        return db_project
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project")
        

@project_router.get("/", response_model=List[ProjectRead])
async def get_all_projects(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.role == Role.ADMIN:
        statement = select(Project)
    else:
        statement = (select(Project)
                     .join(ProjectUserLink, isouter=True)
                     .where(
                         or_(
                             Project.owner_id == current_user.id,
                             and_(
                                 ProjectUserLink.user_id == current_user.id,
                                 ProjectUserLink.project_role == ProjectRole.MANAGER
                             )
                         )
                     ).distinct()
                    )

    projects = session.exec(statement).all()
    return projects

@project_router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: int, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(db_project)
    session.commit()
    return {"detail": "Project deleted successfully"}


##tasks
@project_router.post("/{project_id}/tasks", response_model=TaskReadOnCreate)
async def create_task(project_id: int, data_task: TaskCreate, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    db_user = session.get(User, data_task.assigned_to_id)
    if not db_project or not db_user:
        raise HTTPException(status_code=404, detail="Project or User Not Found")
    if data_task.assigned_to_id != db_project.owner_id:
        if db_user not in db_project.participants:
            raise HTTPException(status_code=400, detail="User is not a participant of the project")
        
    
    db_task = Task(title=data_task.title, description=data_task.description, urgency=data_task.urgency, project_id=project_id, assigned_to_id=data_task.assigned_to_id, status=data_task.status)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    return db_task

@project_router.get("/{project_id}/task/{task_id}", response_model=TaskRead)
async def get_task(project_id: int, task_id: int, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    db_task = session.get(Task, task_id)
    if not db_project or not db_task:
        raise HTTPException(status_code=404, detail="Project or Task Not Founded")
    
    return db_task

@project_router.get("/{project_id}/tasks", response_model=List[TaskRead])
async def get_tasks(project_id: int, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project Not Found")
    return db_project.tasks

@project_router.delete("/{project_id}/task/{task_id}", response_model=dict)
async def delete_task(project_id: int, task_id:int, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    db_task = session.get(Task, task_id)
    if not db_project or not db_task:
        raise HTTPException(status_code=404, detail="Project or Task Not Found")
    session.delete(db_task)
    session.commit()
    return {"detail": f"Task {task_id} deleted successfully"}

@project_router.patch("/{project_id}/task/{task_id}", response_model=TaskRead)
async def update_task(project_id: int, task_id:int, update_task: TaskUpdate, session: Session = Depends(get_session)):
    db_project = session.get(Project, project_id)
    db_task = session.get(Task, task_id)
    if not db_project or not db_task:
        raise HTTPException(status_code=404, detail="Project or Task Not Found")
    if db_task.project_id != db_project.id:
        raise HTTPException(status_code=404, detail="Task does not belogin to this project")
    data_task = update_task.model_dump(exclude_unset=True)
    if "assigned_to_id" in data_task:
        db_user = session.get(User, data_task["assigned_to_id"])
        if not db_user:
            raise HTTPException(status_code=404, detail="User Not Found")
    if update_task.assigned_to_id != db_project.owner_id:
        if db_user not in db_project.participants:
            raise HTTPException(status_code=400, detail="User is not a participant of the project")
        
    db_task.sqlmodel_update(data_task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
    