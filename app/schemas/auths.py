from pydantic import BaseModel


class RefreshTokenSchema(BaseModel):
    refresh_token: str

    class Config:
        schema_extra = {
            'example': {
                'refresh_token': '456',
            }
        }


class AccessTokenSchema(BaseModel):
    access_token: str
    token_type: str ='Bearer'

    class Config:
        schema_extra = {
            'example': {
                'access_token': '123',
                'token_type': 'Bearer',
            }
        }


class TokensSchema(RefreshTokenSchema, AccessTokenSchema):
    pass


class TokenDataSchema(BaseModel):
    user_id: int
    expires: str

    class Config:
        schema_extra = {
            'example': {
                'id': 1,
                'expires': 1686179320.3364985,
            }
        }
