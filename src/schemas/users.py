from pydantic import BaseModel, Field, EmailStr


class UserBaseSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class CreateUserSchema(UserBaseSchema):
    hashed_password: bytes = Field(alias="password")


class UserSchema(UserBaseSchema):
    id: int
    is_active: bool = Field(default=False)

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: EmailStr = Field()
    password: str
