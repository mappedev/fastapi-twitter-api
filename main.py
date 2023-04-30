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

        if any(user_json['email'] == user.email for user_json in results):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exist",
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
def login(user: UserLogin = Body(default=...)) -> User:
    '''
    Login
    
    This path operation login an user in the app.

    Parameters:
    - Request body parameter
        - user: UserLogin
    
    Returns a json with the model user
    '''
    with open('users.json', 'r+', encoding='utf-8') as f:
        results = json.load(f)

        for user_json in results:
            if user_json['email'] == user.email and \
            user_json['password'] == user.password:
                return user_json
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect email or password",
            )

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

    Returns a json list with the user model
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
def get_user(user_id: UUID = Path(default=...)) -> User:
    '''
    Get user

    This path operation get an user in the app.

    Parameters
    - Path parameter
        - user_id: UUID

    Returns a json with the user model
    - id: UUID
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    '''
    with open('users.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

        for user_json in results:
            if user_json['id'] == str(user_id):
                return user_json
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )       

@app.put(
    path='/users/{user_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
    summary='Update user',
)
def update_user(
    user_id: UUID = Path(default=...),
    user: User = Body(default=...),
) -> User:
    '''
    Update user

    This path operation update an user in the app.

    Parameters
        - Path parameter
            - user_id: UUID
        - Request body parameter
            - user: User

    Returns a json with the user model
    - id: UUID
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    '''
    with open('users.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

    for user_json in results:
        if user_json['email'] == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exist",
            )
        if user_json['id'] == str(user_id):
            user_dict = user.dict()
            user_dict['id'] = user_json['id']
            user_dict['password'] = user_json['password']
            user_birth_date = user_dict.get('birth_date', None)
            if user_birth_date:
                user_dict['birth_date'] = str(user_birth_date)
            else:
                user_dict['birth_date'] = user_json['birth_date']

            results[results.index(user_json)] = user_dict

            with open('users.json', 'w', encoding='utf-8') as f:
                f.seek(0)
                json.dump(results, f)

            return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

@app.delete(
    path='/users/{user_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.users],
    summary='Delete user',
)
def delete_user(user_id: UUID = Path(default=...)) -> dict[str, str | bool]:
    '''
    Delete user

    This path operation delete an user in the app.

    Parameters
        - Path parameter
            - user_id: UUID

    Returns a json with the user id and success propery
    - id: UUID
    - success: bool
    '''
    id = str(user_id)
    with open("users.json", "r", encoding="utf-8") as f: 
        results = json.loads(f.read())
    for user_json in results:
        if user_json["id"] == id:
            results.remove(user_json)
            with open("users.json", "w", encoding="utf-8") as f:
                f.seek(0)
                json.dump(results, f)
            return {
                'id': id,
                'success': True,
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

''' Tweets '''
@app.get(
    path='/tweets',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Get all tweets',
)
def get_all_tweets() -> List[Tweet]:
    '''
    Get tweets

    This path operation get all tweets in the app.

    Returns a json list with the tweet model
    - id: UUID
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    '''
    with open('tweets.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
        return results

@app.get(
    path='/tweets/{tweet_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Get tweet',
)
def get_tweet(tweet_id: UUID = Path(default=...)) -> Tweet:
    '''
    Get tweet

    This path operation get a tweet in the app.

    Parameters
    - Path parameter
        - tweet_id: UUID

    Returns a json list with the tweet model
    - id: UUID
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    '''
    with open('tweets.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
        for tweet_json in results:
            if tweet_json['id'] == str(tweet_id):
                return tweet_json
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tweet not found",
            )

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
    
    Returns a json with the tweet model
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
def update_tweet(
    tweet_id: UUID = Path(default=...),
    tweet: Tweet = Body(default=...),
) -> Tweet:
    '''
    Update tweet

    This path operation update a tweet in the app.

    Parameters
        - Path parameter
            - tweet_id: UUID
        - Request body parameter
            - tweet: Tweet

    Returns a json with the tweet model
    - id: UUID
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    '''
    with open('tweets.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

    for tweet_json in results:
        if tweet_json['id'] == str(tweet_id):
            tweet_dict = tweet.dict()
            tweet_dict['id'] = tweet_json['id']
            tweet_dict['created_at'] = tweet_json['created_at']
            tweet_dict['by'] = tweet_json['by']
            tweet_dict['updated_at'] = str(datetime.now())

            results[results.index(tweet_json)] = tweet_dict

            with open('tweets.json', 'w', encoding='utf-8') as f:
                f.seek(0)
                json.dump(results, f)

            return tweet
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found",
        )

@app.delete(
    path='/tweets/{tweet_id}',
    status_code=status.HTTP_200_OK,
    tags=[Tags.tweets],
    summary='Delete tweet',
)
def delete_tweet(tweet_id: UUID = Path(default=...)) -> dict[str, str | bool]:
    '''
    Delete tweet

    This path operation delete a tweet in the app.

    Parameters
    - Path parameter
        - tweet_id: UUID

    Returns a json with the tweet id and success propery
    - id: UUID
    - success: bool
    '''
    id = str(tweet_id)
    with open("tweets.json", "r", encoding="utf-8") as f: 
        results = json.loads(f.read())
    for tweet_json in results:
        if tweet_json["id"] == id:
            results.remove(tweet_json)
            with open("tweets.json", "w", encoding="utf-8") as f:
                f.seek(0)
                json.dump(results, f)
            return {
                'id': id,
                'success': True,
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )
