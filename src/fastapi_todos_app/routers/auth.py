from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..models import User
from passlib.context import CryptContext

# router = APIRouter()

# @router.get("/auth")
# def read_auth():
#     return {"message": "Auth endpoint"}

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: str = Field(..., min_length=5, max_length=100, example="johndoe@example.com")
    first_name: str = Field(..., min_length=1, max_length=50, example="John")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe")
    password: str = Field(..., min_length=8, example="strongpassword123")
    role: str = Field(..., min_length=3, max_length=50, example="user")

@router.post("/auth")
def create_user(create_user_request: CreateUserRequest):
    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    return user