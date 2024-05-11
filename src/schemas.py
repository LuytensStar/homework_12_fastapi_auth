from datetime import date, datetime
from pydantic import BaseModel,Field, EmailStr
from typing import List, Optional

class ContactModel(BaseModel):
    id: int
    name: str = Field(max_length=50, description="Name")
    surname: str = Field(max_length=50, description="Surname")
    electronic_mail: str = Field(max_length=100, description="Email")
    phone_number: str = Field(max_length=20, description="Phone number")
    birth_date: date = Field(description="Date of birth")
    additional_info: Optional[str] = Field( description="Additional info")

class ContactResponse(BaseModel):
    id: int
    name: str
    surname: str
    electronic_mail: str
    phone_number: str
    birth_date: date
    additional_info: Optional[str]

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr
