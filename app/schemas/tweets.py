from datetime import datetime

from pydantic import BaseModel


class TweetBaseSchema(BaseModel):
    content: str

    class Config:
        schema_extra = {"example": {"content": "Hello, World!"}}


class TweetSchema(TweetBaseSchema):
    id: int
    by_id: int
    updated_at: datetime | None
    created_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "content": "Hello, World!",
                "updated_at": "2020-01-01T00:00:00",
                "by_id": 1,
            }
        }


class TweetCreateSchema(TweetBaseSchema):
    by_id: int

    class Config:
        schema_extra = {
            "example": {
                **TweetBaseSchema.Config.schema_extra["example"],
                "by_id": 2,
            }
        }


class TweetUpdateSchema(TweetBaseSchema):
    pass
