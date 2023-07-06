from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import models

from libs.passlib import verify_password


class AuthService:
    async def authenticate(
        self,
        email: str,
        password: str,
        db: AsyncSession,
    ) -> models.User:
        EXCEPTION_401 = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials invalid",
        )

        # user = db.query(models.User).filter(models.User.email == email).first()
        result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        user = result.scalars().first()
        if user is None:
            raise EXCEPTION_401

        password_match = verify_password(
            password=password,
            hashed_password=user.password,
        )
        if not password_match:
            raise EXCEPTION_401

        return user

    async def find_one_by_email_login(
        self,
        email: str,
        db: AsyncSession,
    ) -> models.User:
        # user = db.query(models.User).filter(models.User.email == email).first()
        result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        user = result.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credentials invalid",
            )

        return user
