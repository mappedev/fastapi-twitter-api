from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jwt import decode, encode

from schemas.auths import (
    AccessTokenSchema,
    RefreshTokenSchema,
    TokenDataSchema,
)

from config.settings import settings

at_secr_key = settings.tokens["access_token"]["secret_key"]
at_exp_mins = settings.tokens["access_token"]["expires_mins"]
rt_secr_key = settings.tokens["refresh_token"]["secret_key"]
rt_exp_mins = settings.tokens["refresh_token"]["expires_mins"]
alg = settings.tokens["algorithm"]


def create_access_token(user_id: int) -> AccessTokenSchema:
    expires_in = datetime.utcnow() + timedelta(minutes=at_exp_mins)
    payload = {
        "user_id": user_id,
        "expires": expires_in.isoformat(),
    }
    access_token = encode(payload=payload, key=at_secr_key, algorithm=alg)
    return AccessTokenSchema(access_token=access_token)


def create_refresh_token(user_id: int) -> RefreshTokenSchema:
    expires_in = datetime.utcnow() + timedelta(minutes=at_exp_mins)
    payload = {
        "user_id": user_id,
        "expires": expires_in.isoformat(),
    }
    refresh_token = encode(payload=payload, key=rt_secr_key, algorithm=alg)
    return RefreshTokenSchema(refresh_token=refresh_token)


def decode_token(
    token: str,
    is_refresh_token: bool = False,
) -> TokenDataSchema | None:
    try:
        decoded_token = decode(
            jwt=token,
            key=rt_secr_key if is_refresh_token else at_secr_key,
            algorithms=[alg],
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        expiration_time = datetime.fromisoformat(decoded_token["expires"])
        if datetime.utcnow() > expiration_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenDataSchema(**decoded_token)


def decode_token_without_exception(
    token: str,
    is_refresh_token: bool = False,
) -> TokenDataSchema | None:
    try:
        decoded_token = decode(
            jwt=token,
            key=rt_secr_key if is_refresh_token else at_secr_key,
            algorithms=[alg],
        )
    except:
        return None
    else:
        expiration_time = datetime.fromisoformat(decoded_token["expires"])
        return (
            TokenDataSchema(**decoded_token)
            if expiration_time > datetime.utcnow()
            else None
        )


def get_authorization_header_token(authorization_header: str) -> str | None:
    PREFIX = "Bearer"

    if not authorization_header.startswith(PREFIX):
        return None

    token = authorization_header[len(PREFIX) + 1 :]
    return token
