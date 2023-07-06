from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.commons import get_current_user, get_session
from schemas.users import UserSchema, UserUpdateSchema
from services.users import UserService

from utils.commons import Tags

router = APIRouter(prefix="/users", tags=[Tags.users.value])
service = UserService()


@router.get(
    path="/",
    response_model=List[UserSchema],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    dependencies=[Depends(get_current_user)],
)
async def get_all_users(db: Annotated[AsyncSession, Depends(get_session)]):
    """
    Get users

    This path operation get all users in the app.

    Returns a json list with the user model
    - id: int
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    """
    return await service.find_all(db=db)


@router.get(
    path="/me",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Get me",
)
async def get_me(
    # access_token: Annotated[TokenData, Depends(JWTBearer())],
    user: Annotated[UserSchema, Depends(get_current_user)],
):
    """
    Get me

    This path operation get the current user in the app.

    Returns a json list with the user model
    - id: int
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    """
    return user


@router.get(
    path="/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Get user",
    dependencies=[Depends(get_current_user)],
)
async def get_user(
    user_id: int, db: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Get user

    This path operation get an user in the app.

    Parameters
    - Path parameter
        - user_id: int

    Returns a json with the user model
    - id: int
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    """
    return await service.find_one_by_id(id=user_id, db=db)


@router.put(
    path="/{user_id}",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    dependencies=[Depends(get_current_user)],
)
async def update_user(
    user_id: int,
    user: UserUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Update user

    This path operation update an user in the app.

    Parameters
        - Path parameter
            - user_id: int
        - Request body parameter
            - user: User

    Returns a json with the user model
    - id: int
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: datetime | None
    """
    return await service.update(id=user_id, data=user, db=db)


@router.delete(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    dependencies=[Depends(get_current_user)],
)
async def delete_user(
    user_id: int, db: Annotated[AsyncSession, Depends(get_session)]
) -> dict:
    """
    Delete user

    This path operation delete an user in the app.

    Parameters
        - Path parameter
            - user_id: int

    Returns a json with the user id and success propery
    - id: int
    - success: bool
    """
    return await service.remove(id=user_id, db=db)
