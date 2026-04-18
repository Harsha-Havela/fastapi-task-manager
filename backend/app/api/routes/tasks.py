from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListOut

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task for the authenticated user."""
    task = Task(
        title=payload.title,
        description=payload.description,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=TaskListOut)
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tasks for the authenticated user with optional filtering and pagination."""
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    tasks = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TaskListOut(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific task by ID."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task (title, description, or completion status)."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task by ID."""
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()


@router.get("/stats")
def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task statistics for the authenticated user."""
    total = db.query(Task).filter(Task.owner_id == current_user.id).count()
    completed = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.completed == True
    ).count()
    pending = total - completed
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }
