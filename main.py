from datetime import date, datetime
from enum import Enum
import json
from typing import List
from uuid import uuid4, UUID

from pydantic import BaseModel, EmailStr, Field

from fastapi import Body, FastAPI, HTTPException, Path, status

app = FastAPI()

class Tags(Enum):
    home = 'Home'
    auth = 'Auth'
    users = 'Users'
    tweets = 'Tweets'


class UserBase(BaseModel):
    id: UUID = Field(default_factory=uuid4) # añadimos default_factory
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


class UserRegister(User, UserLogin):
    pass


class Tweet(BaseModel):
    id: UUID = Field(default_factory=uuid4)
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
def signup(user: UserRegister = Body(default=...)) -> User:
    '''
    Signup

    This path operation register an user in the app.
    
    Parameters:
    - Request body parameter
        - user: UserRegister
    
    Returns a json with the user model
    - id: UUID
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: date
    '''
    with open('users.json', 'r+', encoding='utf-8') as f:
        # results = json.loads(f.read()) # loads load a string
        results = json.load(f)

        if any(userJson['email'] == user.email for userJson in results):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exist!",
            )

        user_dict = user.dict()
        user_dict['id'] = str(uuid4())
        user_birth_date = user_dict.get('birth_date', None)
        if user_birth_date:
            user_dict['birth_date'] = str(user_birth_date)
            
        results.append(user_dict)
        f.seek(0)
        json.dump(results, f)

        return user

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
    '''
    Get users

    This path operation get all users in the app.

    Returns a list json with the user model
    - id: UUID
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    '''
    with open('users.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
        return results

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
@app.get(
    path='/tweets',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Get all tweets',
)
def get_all_tweets() -> List[Tweet]:
    return [Tweet()]

@app.get(
    path='/tweets/{tweet_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Get tweet',
)
def get_tweet(tweet_id: int = Path(
    default=...,
    ge=1,
)) -> Tweet:
    return Tweet()

@app.post(
    path='/tweets',
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.tweets],
    summary='Create tweet',
)
def create_tweet(tweet: Tweet = Body(default=...)) -> Tweet:
    '''
    Post tweet

    This path operation post a tweet in the app.

    Parameters:
    - Request body parameter
        - tweet: Tweet
    
    Returns a model tweet
    - id: UUID
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    '''
    with open('tweets.json', 'r+', encoding='utf-8') as f:
        results = json.load(f)

        tweet_dict = tweet.dict()
        tweet_dict['id'] = str(uuid4())

        tweet_created_at = tweet_dict.get('created_at', None) 
        if tweet_created_at:
            tweet_dict['created_at'] = str(tweet_created_at)

        tweet_updated_at = tweet_dict.get('updated_at', None) 
        if tweet_updated_at:
            tweet_dict['updated_at'] = str(tweet_updated_at)
        
        tweet_dict['by']['id'] = str(tweet_dict['by']['id'])
        tweet_dict['by']['birth_date'] = str(tweet_dict['by']['birth_date'])

        results.append(tweet_dict)
        f.seek(0)
        json.dump(results, f)

        return tweet


@app.put(
    path='/tweets/{tweet_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Update tweet',
)
def update_tweet(tweet_id: int = Path(
    default=...,
    ge=1,
)) -> Tweet:
    return Tweet()

@app.delete(
    path='/tweets/{tweet_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Delete tweet',
)
def delete_tweet(tweet_id: int = Path(
    default=...,
    ge=1,
)) -> Tweet:
    return Tweet()
