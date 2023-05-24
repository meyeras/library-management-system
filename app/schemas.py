from pydantic import BaseModel, EmailStr
from pydantic.types import Optional
from typing import List

class UserBase(BaseModel):
    username: str
    email: EmailStr
 

class UserCreate(UserBase):
    password: str

class UserUpdateRequest(BaseModel):
    password: str = None
    username: str = None
    email: EmailStr = None


class UserUpdateResponse(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode=True


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class BookBaseSchema(BaseModel):
    id: int
    title: str
    author: str
    isbn: str

    @classmethod
    def from_model(cls, book):
        print("Enter in BookBaseSchema from_model")
        author_name = book.author.name if book.author else None
        print("BookBaseSchema: author name {0}".format(author_name))
        return cls(id=book.id, title=book.title, isbn=book.isbn, author=author_name)
    

class BooksResponseSchema(BaseModel):
    books: List[BookBaseSchema] = []
    page: int = 1
    count: int
    has_more: bool = None

class BookCreateSchema(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int = 1

class BookUpdateSchema(BaseModel):
    title: str = None
    author: str = None
    isbn: str = None
    copies: int = None
 

class BookDetailsResponseSchema(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    num_copies: Optional[int] = None
    num_borrowed_copies: Optional[int] = None



class BookQueryParams(BaseModel):
    title: Optional[str]
    author: Optional[str]
    available: Optional[bool]