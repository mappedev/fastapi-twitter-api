from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.commons import get_current_user, get_session
from schemas.tweets import (
    TweetSchema,
    TweetCreateSchema,
    TweetUpdateSchema,
)
from services.tweets import TweetService

from utils.commons import Tags

router = APIRouter(
    prefix="/tweets",
    tags=[Tags.tweets.value],
    dependencies=[Depends(get_current_user)],
)
service = TweetService()


@router.get(
    path="/",
    response_model=List[TweetSchema],
    status_code=status.HTTP_200_OK,
    summary="Get all tweets",
)
async def get_all_tweets(db: Annotated[AsyncSession, Depends(get_session)]):
    """
    Get tweets

    This path operation get all tweets in the app.

    Returns a json list with the tweet model
    - id: int
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    """
    return await service.find_all(db=db)


@router.get(
    path="/{tweet_id}",
    response_model=TweetSchema,
    status_code=status.HTTP_200_OK,
    summary="Get tweet",
)
async def get_tweet(
    tweet_id: int, db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Get tweet

    This path operation get a tweet in the app.

    Parameters
    - Path parameter
        - tweet_id: int

    Returns a json list with the tweet model
    - id: int
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    """
    return await service.find_one_by_id(id=tweet_id, db=db)


@router.post(
    path="/",
    response_model=TweetSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create tweet",
)
async def create_tweet(
    tweet: TweetCreateSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Post tweet

    This path operation post a tweet in the app.

    Parameters:
    - Request body parameter
        - tweet: Tweet

    Returns a json with the tweet model
    - id: int
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    """
    return await service.create(data=tweet, db=db)


@router.put(
    path="/{tweet_id}",
    response_model=TweetSchema,
    status_code=status.HTTP_200_OK,
    summary="Update tweet",
)
async def update_tweet(
    tweet_id: int,
    tweet: TweetUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Update tweet

    This path operation update a tweet in the app.

    Parameters
        - Path parameter
            - tweet_id: int
        - Request body parameter
            - tweet: Tweet

    Returns a json with the tweet model
    - id: int
    - content: str
    - created_at: datetime
    - updated_at: datetime | None
    - by: User
    """
    return await service.update(id=tweet_id, data=tweet, db=db)


@router.delete(
    path="/{tweet_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete tweet",
)
async def delete_tweet(
    tweet_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """
    Delete tweet

    This path operation delete a tweet in the app.

    Parameters
    - Path parameter
        - tweet_id: int

    Returns a json with the tweet id and success propery
    - id: int
    - success: bool
    """
    return await service.remove(id=tweet_id, db=db)
