from datetime import date

from pydantic import BaseModel, EmailStr


class UserBaseSchema(BaseModel):
    email: EmailStr

    class Config:
        schema_extra = {"example": {"email": "mappedev@gmail.com"}}


class UserSchema(UserBaseSchema):
    id: int
    first_name: str
    last_name: str
    birth_date: date | None = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                **UserBaseSchema.Config.schema_extra["example"],
                "first_name": "Mario",
                "last_name": "Peña",
                "birth_date": "1997-03-29",
            }
        }


class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: str | None = None

    def filter_fields_to_update(self) -> dict:
        values = {}
        for k, v in self.dict().items():
            if v is not None:
                values[k] = v

        return values

    class Config:
        schema_extra = {"example": {"first_name": "Mario"}}


class UserLoginSchema(UserBaseSchema):
    password: str

    class Config:
        schema_extra = {
            "example": {
                **UserBaseSchema.Config.schema_extra["example"],
                "password": "12345678",
            }
        }


class UserRegisterSchema(UserSchema, UserLoginSchema):
    id: int | None

    class Config:
        schema_extra = {
            "example": {
                **UserBaseSchema.Config.schema_extra["example"],
                **UserSchema.Config.schema_extra["example"],
                **UserLoginSchema.Config.schema_extra["example"],
            }
        }
