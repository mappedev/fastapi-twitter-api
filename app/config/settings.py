import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    databases = {"url": os.getenv("DB_URL")}
    tokens = {
        "access_token": {
            "secret_key": os.getenv("ACCESS_SECRET_KEY"),
            "expires_mins": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINS", 30)),
        },
        "refresh_token": {
            "secret_key": os.getenv("REFRESH_SECRET_KEY"),
            "expires_mins": int(
                os.getenv(
                    "REFRESH_TOKEN_EXPIRE_MINS",
                    60 * 24 * 7,
                )
            ),
        },
        "algorithm": os.getenv("ALGORITHM", "HS256"),
    }

    class Config:
        env_file = ".env"


settings = Settings()
