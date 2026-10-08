from fastapi import FastAPI, Path, Query, HTTPException
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Post:
    id: str
    title: str
    content: str
    rating: int

    def __init__(self, title: str, content: str, rating: int):
        self.id = str(uuid4())
        self.title = title
        self.content = content
        self.rating = rating

class PostRequest(BaseModel):
    id: Optional[str] = Field(default=None, example="123e4567-e89b-12d3-a456-426614174000")
    title: str = Field(..., min_length=3, example="New Post Title")
    content: str = Field(..., min_length=3, max_length=100, example="Content of the new post")
    rating: int = Field(..., ge=1, le=5, example=5)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "New Post Title",
                "content": "Content of the new post",
                "rating": 5
            }
        }
    }

POSTS = [
    Post(title="First Post", content="Content of the first post", rating=5),
    Post(title="Second Post", content="Content of the second post", rating=4),
]

@app.get("/posts", status_code=status.HTTP_200_OK)
async def get_posts():
    return POSTS

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

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post_request: PostRequest):
    # new_post = Post(title=post_request.title, content=post_request.content, rating=post_request.rating)
    new_post = Post(**post_request.model_dump())
    POSTS.append(new_post)
    return new_post

@app.put("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(post_id: str, post_request: PostRequest):
    post_changed = False

    for post in POSTS:
        if post.id == post_id:
            post.title = post_request.title
            post.content = post_request.content
            post.rating = post_request.rating
            post_changed = True
            # return post
    if not post_changed:
        raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: str):
    post_changed = False

    for post in POSTS:
        if post.id == post_id:
            POSTS.remove(post)
            post_changed = True
            # return {"message": "Post deleted successfully"}
    if not post_changed:
        raise HTTPException(status_code=404, detail="Post not found")


"""
Status Codes:

2xx Success Status Codes:
- 200: OK
- 201: Created
- 204: No Content

4xx Client Error Status Codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

5xx Server Error Status Codes:
- 500: Internal Server Error
"""