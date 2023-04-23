from enum import Enum
from uuid import UUID
from datetime import date

from pydantic import BaseModel, EmailStr, Field

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class Tags(Enum):
    home = 'Home'


class UserBase(BaseModel):
    id: UUID = Field(default=...)
    email: EmailStr = Field(default=..., example='mappedev@gmail.com')


class UserLogin(UserBase):
    password: str = Field(
        default=...,
        min_length=8,
        max_length=64,
        example='12345678',
    )


class User(UserBase):
    first_name: str = Field(
        default=...,
        min_length=1,
        max_length=50,
        example='Mario',
    )
    last_name: str = Field(
        default=...,
        min_length=1,
        max_length=50,
        example='Peña'
    )
    birth_date: date | None = Field(
        default=None,
        example='1997-03-29'
    )


class Tweet(BaseModel):
    pass


@app.get(
    path='/',
    status_code=status.HTTP_200_OK,
    tags=[Tags.home],
    summary='Home',
)
def home() -> dict[str, str]:
    return {'Twitter API': 'Working!'}
