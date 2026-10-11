from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todo
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field

router = APIRouter()

def get_db():
    db = SessionLocal()
    # On every request database session is created and closed after use
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(..., description="The title of the todo", example="Buy groceries", min_length=10)
    description: str = Field(..., description="The description of the todo", example="Buy milk, eggs, and bread", min_length=10, max_length=200)
    priority: int = Field(..., description="The priority of the todo", example=3, gt=0, lt=6)
    completed: bool = Field(..., description="The completion status of the todo", example=False)

@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency):
    return db.query(Todo).all()

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0, description="The ID of the todo to retrieve")):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    # todo = Todo(
    #     title=todo_request.title,
    #     description=todo_request.description,
    #     priority=todo_request.priority,
    #     completed=todo_request.completed
    # )
    todo = Todo(**todo_request.model_dump())
    db.add(todo)
    db.commit()
    # db.refresh(todo)
    return todo

@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0, description="The ID of the todo to update")):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    # for key, value in todo_request.model_dump().items():
    #     setattr(todo, key, value)
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed
    db.add(todo)
    db.commit()
    # db.refresh(todo)

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0, description="The ID of the todo to delete")):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()