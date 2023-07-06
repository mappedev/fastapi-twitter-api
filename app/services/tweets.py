from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import models
from schemas.tweets import TweetCreateSchema, TweetUpdateSchema


class TweetService(object):
    TWEET_EXCEPTION_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Tweet not found",
    )
    USER_EXCEPTION_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

    async def find_all(self, db: AsyncSession) -> Sequence[models.Tweet]:
        # tweets = db.query(models.Tweet).all()
        result = await db.execute(
            select(models.Tweet).order_by(models.Tweet.id.desc())
        )
        tweets = result.scalars().all()
        return tweets

    async def find_one_by_id(self, id: int, db: AsyncSession) -> models.Tweet:
        # tweet = db.query(models.Tweet).filter(models.Tweet.id == id).first()
        result = await db.execute(
            select(models.Tweet).filter(models.Tweet.id == id)
        )
        tweet = result.scalars().first()
        if tweet is None:
            raise self.TWEET_EXCEPTION_404

        return tweet

    async def create(
        self,
        data: TweetCreateSchema,
        db: AsyncSession,
    ) -> models.Tweet:
        # exists = (
        #     db.query(models.User).filter(models.User.id == data.by_id).first()
        #     is not None
        # )
        result = await db.execute(
            select(models.Tweet).filter(models.Tweet.id == id)
        )
        exists = result.scalars().first() is not None
        if not exists:
            raise self.USER_EXCEPTION_404

        tweet = models.Tweet(**data.dict(exclude_unset=True))
        db.add(tweet)
        await db.commit()
        await db.refresh(tweet)
        return tweet

    async def update(
        self,
        id: int,
        data: TweetUpdateSchema,
        db: AsyncSession,
    ) -> models.Tweet:
        # tweet = db.query(models.Tweet).filter(models.Tweet.id == id).first()
        result = await db.execute(
            select(models.Tweet).filter(models.Tweet.id == id)
        )
        tweet = result.scalars().first()
        if tweet is None:
            raise self.TWEET_EXCEPTION_404

        tweet.content = data.content
        await db.commit()
        await db.refresh(tweet)
        return tweet

    async def remove(self, id: int, db: AsyncSession) -> dict:
        # tweet = db.query(models.Tweet).filter(models.Tweet.id == id).first()
        result = await db.execute(
            select(models.Tweet).filter(models.Tweet.id == id)
        )
        tweet = result.scalars().first()
        if tweet is None:
            raise self.TWEET_EXCEPTION_404

        await db.delete(tweet)
        await db.commit()
        return {"id": id, "success": True}
