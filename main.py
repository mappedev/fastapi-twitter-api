from datetime import date, datetime
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from fastapi import FastAPI, Path, status

app = FastAPI()

class Tags(Enum):
    home = 'Home'
    auth = 'Auth'
    users = 'Users'
    tweets = 'Tweets'


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
    id: UUID = Field(default=...)
    content: str = Field(
        default=...,
        min_length=1,
        max_length=256,
        example='Hola',
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=None)
    by: User = Field(default=...,)


''' Path operations'''
@app.get(
    path='/',
    status_code=status.HTTP_200_OK,
    tags=[Tags.home],
    summary='Home',
)
def home() -> dict[str, str]:
    return {'Twitter API': 'Working!'}

''' Auth '''
@app.post(
    path='/auth/signup',
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.auth],
    summary='Register a user',
)
def signup() -> User:
    return User()

@app.post(
    path='/auth/login',
    status_code=status.HTTP_200_OK,
    tags=[Tags.auth],
    summary='Login a user',
)
def login() -> UserLogin:
    return UserLogin()

''' Users '''
@app.get(
    path='/users',
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
    summary='Get all users',
)
def get_all_users() -> List[User]:
    return [User()]

@app.get(
    path='/users/{user_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
    summary='Get user',
)
def get_user(user_id: int = Path(
    default=...,
    ge=1,
)) -> User:
    return User()

@app.post(
    path='/users',
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.users],
    summary='Create user',
)
def create_user(user_id: int = Path(
    default=...,
    ge=1,
)) -> User:
    return User()

@app.put(
    path='/users/{user_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
    summary='Update user',
)
def update_user(user_id: int = Path(
    default=...,
    ge=1,
)) -> User:
    return User()

@app.delete(
    path='/users/{user_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
    summary='Delete user',
)
def delete_user(user_id: int = Path(
    default=...,
    ge=1,
)) -> User:
    return User()

''' Tweets '''
