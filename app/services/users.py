from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# from models.users import User
from db import models
from schemas.users import UserRegisterSchema, UserUpdateSchema

from libs.passlib import create_password_hash


class UserService(object):
    EXCEPTION_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

    async def find_all(self, db: AsyncSession) -> Sequence[models.User]:
        # users = db.query(models.User).all()
        result = await db.execute(
            select(models.User).order_by(models.User.id.desc())
        )
        users = result.scalars().all()
        return users

    async def find_one_by_id(self, id: int, db: AsyncSession) -> models.User:
        # user = db.query(models.User).filter(models.User.id == id).first()
        result = await db.execute(
            select(models.User).where(models.User.id == id)
        )
        user = result.scalars().first()
        if user is None:
            raise self.EXCEPTION_404

        return user

    async def find_one_by_email(
        self, email: str, db: AsyncSession
    ) -> models.User:
        # user = db.query(models.User).filter(models.User.email == email).first()
        result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        user = result.scalars().first()
        if user is None:
            raise self.EXCEPTION_404

        return user

    async def create(
        self,
        data: UserRegisterSchema,
        db: AsyncSession,
    ) -> models.User:
        # exists = (
        #     db.query(models.User)
        #     .filter(models.User.email == data.email)
        #     .first()
        #     is not None
        # )
        result = await db.execute(
            select(models.User).where(models.User.email == data.email)
        )
        exists = result.scalars().first() is not None
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        data.password = create_password_hash(data.password)
        user = models.User(**data.dict(exclude_unset=True))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update(
        self,
        id: int,
        data: UserUpdateSchema,
        db: AsyncSession,
    ) -> models.User:
        # user = db.query(models.User).filter(models.User.id == id).first()
        result = await db.execute(
            select(models.User).where(models.User.id == id)
        )
        user = result.scalars().first()
        if user is None:
            raise self.EXCEPTION_404

        update_data = data.filter_fields_to_update()
        for k, v in update_data.items():
            setattr(user, k, v)

        await db.commit()
        await db.refresh(user)
        return user

    async def remove(self, id: int, db: AsyncSession) -> dict:
        # user = db.query(models.User).filter(models.User.id == id).first()
        result = await db.execute(
            select(models.User).where(models.User.id == id)
        )
        user = result.scalars().first()
        if user is None:
            raise self.EXCEPTION_404

        await db.delete(user)
        await db.commit()
        return {"id": id, "success": True}
