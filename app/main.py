from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .routers import books, users, borrows, login
from app import models
from app.middlewares import catch_exceptions_middleware

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(borrows.router, tags=["Borrows"])
app.include_router(login.router, tags=["Users"])

app.middleware("http")(catch_exceptions_middleware)


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    