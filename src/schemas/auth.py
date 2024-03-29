from src.schemas.users import UserBaseSchema
from typing import List
from pydantic import BaseModel, Field, EmailStr


class RegisterSchema(UserBaseSchema):
    hashed_password: bytes = Field(alias="password")


class LoginSchema(BaseModel):
    email: EmailStr = Field()
    password: str

class EmailSchema(BaseModel):
    email: EmailStr

class CheckUserExistsSchema(BaseModel):
    email: EmailStr

class OTPCreateSchema(BaseModel):
    email: EmailStr
    token: str

class OTPCheckSchema(BaseModel):
    email: EmailStr
    token: str
    
class LogoutSchema(BaseModel):
    access_token: str

from pydantic import BaseModel, EmailStr, Field

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str
    retype_password: str