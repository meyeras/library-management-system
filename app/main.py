from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .routers import books, users, borrows, login
from app import models
from sqlalchemy.exc import SQLAlchemyError

from app.middlewares import SQLAlchemyToPydanticMiddleware
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc):
    # Handle the database connection error here
    # You can log the error, return custom error responses, etc.
    return {"detail": "Database Connection Error"}


app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(borrows.router, prefix="/borrows", tags=["Borrows"])
app.include_router(login.router, tags=["Users"])

#app.add_middleware(SQLAlchemyToPydanticMiddleware)

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

    