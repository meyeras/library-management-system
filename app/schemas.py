from pydantic import BaseModel, EmailStr
from pydantic.types import Optional
from typing import List
from datetime import datetime


def trim_whitespace(data):
        if isinstance(data, str):
            return data.strip()
        elif isinstance(data, list):
            return [trim_whitespace(item) for item in data]
        elif isinstance(data, dict):
            return {k: trim_whitespace(v) for k, v in data.items()}
        else:
            return data
        

class BaseSchema(BaseModel):
    def trim_data(self):
        # Convert the data to a dictionary
        data_dict = self.dict()
        # Perform the desired manipulations on the dictionary
        modified_dict = trim_whitespace(data_dict)
        # Convert the modified dictionary back to the Pydantic model
        modified_data = self.__class__(**modified_dict)
        return modified_data

class UserBase(BaseSchema):
    username: str
    email: EmailStr
 

class UserCreate(UserBase):
    password: str

class UserUpdateRequest(BaseSchema):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]


class UserSchema(BaseSchema):
    id: int
    username: str
    email: str
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseSchema):
    access_token: str
    token_type: str


class BookBaseSchema(BaseSchema):
    id: int
    title: str
    author: str
    isbn: str

    @classmethod
    def from_model(cls, book):
        author_name = book.author.name if book.author else None
        return cls(id=book.id, title=book.title, isbn=book.isbn, author=author_name)
    

class BooksResponseSchema(BaseSchema):
    books: List[BookBaseSchema] = []
    page: int = 1
    count: int
    has_more: bool = None

class BookCreateSchema(BaseSchema):
    title: str
    author: str
    isbn: str
    copies: int = 1

class BookUpdateSchema(BaseSchema):
    title: str = None
    author: str = None
    isbn: str = None
    copies: int = None
 

class BookDetailsResponseSchema(BaseSchema):
    id: int
    title: str
    author: str
    isbn: str
    num_copies: Optional[int]
    num_borrowed_copies: Optional[int]

class BookQueryParams(BaseSchema):
    title: Optional[str]
    author: Optional[str]
    available: Optional[bool]


class BorrowResponse(BaseSchema):
    book_id: int
    book_title: str
    author: str
    borrow_date: datetime
    remaining_days: int
    fine_amount: float

class BorrowsListResponse(BaseSchema):
    borrows: List[BorrowResponse]
    count: int = 0
    total_fine_amount: float