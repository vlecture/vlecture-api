from src.schemas.users import UserBaseSchema
from pydantic import BaseModel, Field, EmailStr


class RegisterSchema(UserBaseSchema):
    hashed_password: bytes = Field(alias="password")


class LoginSchema(BaseModel):
    email: EmailStr = Field()
    password: str

class LogoutSchema(BaseModel):
    access_token: str