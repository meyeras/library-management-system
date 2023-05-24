from pydantic import BaseModel, EmailStr
from pydantic.types import Optional

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

