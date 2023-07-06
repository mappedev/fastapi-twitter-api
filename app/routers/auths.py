from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.commons import get_session
from schemas.auths import (
    AccessTokenSchema,
    RefreshTokenSchema,
    TokensSchema,
)
from schemas.users import UserSchema, UserRegisterSchema
from services.auths import AuthService
from services.users import UserService

from libs.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from utils.commons import Tags


router = APIRouter(prefix="/auths", tags=[Tags.auths.value])
auth_service = AuthService()
user_service = UserService()


@router.post(
    path="/signup",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
async def signup(
    user: UserRegisterSchema,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Signup

    This path operation register an user in the app.

    Parameters:
    - Request body parameter
        - user: UserRegister

    Returns a json with the user model
    - id: int
    - email: EmailStr
    - first_name: str
    - last_name: str
    - birth_day: date
    """
    return await user_service.create(data=user, db=db)


@router.post(
    path="/login",
    response_model=TokensSchema,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
)
async def login(
    # user: UserLoginSchema,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Login

    This path operation login an user in the app.

    Parameters:
    - Request body parameter
        - user: UserLogin

    Returns a json with the model user
    """
    # user_obj = await service.authenticate(email=user.email, password=user.password)
    user = await auth_service.authenticate(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    return TokensSchema(
        **access_token.dict(),
        **refresh_token.dict(),
    )


@router.post(
    path="/refresh",
    response_model=AccessTokenSchema,
    status_code=status.HTTP_200_OK,
    summary="Get new access token",
)
def get_new_access_token(token: RefreshTokenSchema):
    """
    Refresh token

    This path operation get a new access token from a refresh token in the app.

    Parameters:
    - Request body parameter
        - access_token: AccessTokenSchema

    Returns a json with the access token
    """
    ref_tok_data = decode_token(
        token=token.refresh_token,
        is_refresh_token=True,
    )
    return create_access_token(user_id=ref_tok_data.user_id)
