from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session
from services.users import UserService
from schemas.users import UserSchema

from libs.jwt import decode_token

oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/v1/auths/login")
service = UserService()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# def get_db() Session:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_schema)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserSchema:
    acc_tok_data = decode_token(token=access_token)
    return await service.find_one_by_id(db=db, id=acc_tok_data.user_id)
