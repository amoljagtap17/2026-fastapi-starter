from fastapi import FastAPI
from uuid import uuid4
from pydantic import BaseModel

app = FastAPI()

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: str

POSTS: list[Post] = []

# Get requests for all posts
@app.get("/posts")
async def get_posts():
    return POSTS

# Query Parameter for searching posts by title
@app.get("/posts/filter")
async def search_posts(title: str):
    results = []
    for post in POSTS:
        if title.casefold() in post.title.casefold():
            results.append(post)
    return results

"""
Explanation:
The "/posts/filter" route must be defined before the "/posts/{post_id}" route to avoid conflicts.
This ensures that the filter route is matched first before the dynamic post_id route.
If the order is reversed, a request to "/posts/filter" would be interpreted as a request to "/posts/{post_id}" with "filter" as the post_id.
Therefore, always define the more specific routes before the more general ones.
If no path parameters, arguments are treated as query parameters.
"""

# Path Parameter for a single post
@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    for post in POSTS:
        if post["id"].casefold() == post_id.casefold():
            return post
    return {"error": "Post not found"}


# Post request to create a new post
@app.post("/posts")
async def create_post(post: PostCreate):
    new_post = Post(id=str(uuid4()), title=post.title, content=post.content)
    POSTS.append(new_post)
    return new_post

# Put request to update an existing post
@app.put("/posts/{post_id}")
async def update_post(post_id: str, updated_post: PostCreate):
    """
    for i in range(len(POSTS)):
        if POSTS[i].id.casefold() == post_id.casefold():
            POSTS[i] = Post(id=POSTS[i].id, title=updated_post.title, content=updated_post.content)
            return POSTS[i]
    return {"error": "Post not found"}
    """
    for index, post in enumerate(POSTS):
        if post.id.casefold() == post_id.casefold():
            POSTS[index] = Post(id=post.id, title=updated_post.title, content=updated_post.content)
            return POSTS[index]
    return {"error": "Post not found"}

# Delete request to remove an existing post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    for index, post in enumerate(POSTS):
        if post.id.casefold() == post_id.casefold():
            deleted_post = POSTS.pop(index)
            return deleted_post
    return {"error": "Post not found"}