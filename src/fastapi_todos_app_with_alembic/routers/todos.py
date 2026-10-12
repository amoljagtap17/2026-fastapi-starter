from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todo
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

def get_db():
    db = SessionLocal()
    # On every request database session is created and closed after use
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(..., description="The title of the todo", example="Buy groceries", min_length=10)
    description: str = Field(..., description="The description of the todo", example="Buy milk, eggs, and bread", min_length=10, max_length=200)
    priority: int = Field(..., description="The priority of the todo", example=3, gt=0, lt=6)
    completed: bool = Field(..., description="The completion status of the todo", example=False)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
    # return db.query(Todo).all()
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0, description="The ID of the todo to retrieve")):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()

    if todo is not None:
        return todo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    # todo = Todo(
    #     title=todo_request.title,
    #     description=todo_request.description,
    #     priority=todo_request.priority,
    #     completed=todo_request.completed
    # )
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo = Todo(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0, description="The ID of the todo to update")):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    
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
    db.refresh(todo)
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0, description="The ID of the todo to delete")):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).delete()
    # db.delete(todo)
    db.commit()
    # db.refresh(todo)
    # return todo