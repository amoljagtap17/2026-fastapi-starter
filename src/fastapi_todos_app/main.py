from fastapi import FastAPI
from . import models
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}