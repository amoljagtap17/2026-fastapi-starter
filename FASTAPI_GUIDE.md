# FastAPI Implementation Guide

A summary of the FastAPI patterns used across this repo's example apps, with real code snippets pulled from the source. Use this as a quick reference for request handling, validation, routing, database access, and authentication.

## Creating a New App

A FastAPI app starts with an `app = FastAPI()` instance. See [fastapi_starter/__init__.py](./src/fastapi_starter/__init__.py):

```python
from fastapi import FastAPI

app = FastAPI()
```

Run it with the entrypoint configured in [pyproject.toml](./pyproject.toml) under `[tool.fastapi]`, then:

```bash
uv run fastapi dev
```

For larger apps, split routes into routers and include them on the main app. See [fastapi_todos_app/main.py](./src/fastapi_todos_app/main.py):

```python
from fastapi import FastAPI
from .database import engine
from .routers import auth, todos, admin, users
from .models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
```

Each router groups related endpoints under a shared prefix and tag. See [fastapi_todos_app/routers/todos.py](./src/fastapi_todos_app/routers/todos.py):

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)
```

## GET Requests

### Simple GET (return a list)

From [fastapi_starter/__init__.py](./src/fastapi_starter/__init__.py):

```python
@app.get("/posts")
async def get_posts():
    return POSTS
```

### GET with a path parameter

```python
@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    for post in POSTS:
        if post["id"].casefold() == post_id.casefold():
            return post
    return {"error": "Post not found"}
```

> **Route ordering matters:** a static route like `/posts/filter` must be declared *before* a dynamic route like `/posts/{post_id}`, otherwise the dynamic route swallows the request and treats `"filter"` as a `post_id`.

### GET with a query parameter

```python
@app.get("/posts/filter")
async def search_posts(title: str):
    results = []
    for post in POSTS:
        if title.casefold() in post.title.casefold():
            results.append(post)
    return results
```

### Validated path/query parameters with `Path` and `Query`

From [fastapi_oop/__init__.py](./src/fastapi_oop/__init__.py):

```python
from fastapi import FastAPI, Path, Query, HTTPException
from starlette import status

@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(post_id: str = Path(title="The ID of the post to retrieve")):
    for post in POSTS:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.get("/posts/filter", status_code=status.HTTP_200_OK)
async def filter_posts(rating: int = Query(title="The rating to filter posts by", ge=1, le=5)):
    filtered_posts = [post for post in POSTS if post.rating == rating]
    return filtered_posts
```

### GET with dependency injection (DB session + current user)

From [fastapi_todos_app/routers/todos.py](./src/fastapi_todos_app/routers/todos.py):

```python
from typing import Annotated
from fastapi import Depends, HTTPException, Path
from sqlalchemy.orm import Session
from .auth import get_current_user

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
```

## POST Requests

### Basic POST with a Pydantic request body

From [fastapi_starter/__init__.py](./src/fastapi_starter/__init__.py):

```python
from pydantic import BaseModel
from uuid import uuid4

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: str

@app.post("/posts")
async def create_post(post: PostCreate):
    new_post = Post(id=str(uuid4()), title=post.title, content=post.content)
    POSTS.append(new_post)
    return new_post
```

### POST with field validation and an explicit status code

From [fastapi_oop/__init__.py](./src/fastapi_oop/__init__.py):

```python
from pydantic import BaseModel, Field
from typing import Optional

class PostRequest(BaseModel):
    id: Optional[str] = Field(default=None, example="123e4567-e89b-12d3-a456-426614174000")
    title: str = Field(..., min_length=3, example="New Post Title")
    content: str = Field(..., min_length=3, max_length=100, example="Content of the new post")
    rating: int = Field(..., ge=1, le=5, example=5)

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post_request: PostRequest):
    new_post = Post(**post_request.model_dump())
    POSTS.append(new_post)
    return new_post
```

### POST that writes to a database

From [fastapi_todos_app/routers/todos.py](./src/fastapi_todos_app/routers/todos.py):

```python
class TodoRequest(BaseModel):
    title: str = Field(..., min_length=10)
    description: str = Field(..., min_length=10, max_length=200)
    priority: int = Field(..., gt=0, lt=6)
    completed: bool = Field(...)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    todo = Todo(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo
```

### POST for authentication (login/token issuance)

From [fastapi_todos_app/routers/auth.py](./src/fastapi_todos_app/routers/auth.py):

```python
from fastapi.security import OAuth2PasswordRequestForm

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
```

## PUT Requests

From [fastapi_todos_app/routers/todos.py](./src/fastapi_todos_app/routers/todos.py):

```python
@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo
```

> A `204 No Content` response body is ignored by clients, but the examples above still return the object for convenience during development.

## DELETE Requests

From [fastapi_todos_app/routers/todos.py](./src/fastapi_todos_app/routers/todos.py):

```python
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).delete()
    db.commit()
```

## Status Codes Cheat Sheet

From [fastapi_oop/__init__.py](./src/fastapi_oop/__init__.py):

```
2xx Success
- 200: OK
- 201: Created
- 204: No Content

4xx Client Error
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

5xx Server Error
- 500: Internal Server Error
```

## Database Access with SQLAlchemy

### Engine and session setup

From [fastapi_todos_app/database.py](./src/fastapi_todos_app/database.py):

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

> `connect_args={'check_same_thread': False}` is only needed for SQLite; omit it for PostgreSQL.

### Models

From [fastapi_todos_app/models.py](./src/fastapi_todos_app/models.py):

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

### Per-request DB session dependency

Used in every router (e.g. [fastapi_todos_app/routers/todos.py](./src/fastapi_todos_app/routers/todos.py)):

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
```

## JWT Authentication

From [fastapi_todos_app/routers/auth.py](./src/fastapi_todos_app/routers/auth.py):

```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = '...'   # generate with: openssl rand -hex 32
ALGORITHM = 'HS256'

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        user_role = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
```

`get_current_user` is then used as a dependency (`user_dependency`) in protected routes to identify the caller and enforce role checks, e.g. in [fastapi_todos_app/routers/admin.py](./src/fastapi_todos_app/routers/admin.py):

```python
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todo).all()
```

## Summary of Key Concepts

| Concept | Example |
|---|---|
| App instance | `app = FastAPI()` |
| Router with prefix/tags | `APIRouter(prefix="/todos", tags=["todos"])` |
| Path parameter | `@app.get("/posts/{post_id}")` |
| Query parameter | plain function argument (`title: str`) not in the path |
| Validated params | `Path(gt=0)`, `Query(ge=1, le=5)` |
| Request body validation | Pydantic `BaseModel` with `Field(...)` |
| Response status code | `@router.post("/", status_code=status.HTTP_201_CREATED)` |
| Dependency injection | `Annotated[Session, Depends(get_db)]` |
| Auth dependency | `Annotated[dict, Depends(get_current_user)]` |
| Error handling | `raise HTTPException(status_code=404, detail="...")` |
| DB session lifecycle | `get_db()` generator with `yield` + `finally: db.close()` |
| Password hashing | `CryptContext(schemes=["bcrypt"])` |
| JWT issuance/validation | `jose.jwt.encode` / `jose.jwt.decode` |
