from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import engine

from .routers import books, users, borrows

app = FastAPI()

app.include_router(books.router, tags=["Books"])
app.include_router(users.router, tags=["Users"])
app.include_router(borrows.router, tags=["Borrows"])


origins = [
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/books")
def get_all_books():
    return [{"Book title": "some title" ,"Book author": "some author", "Book isbn": 93838}]

    