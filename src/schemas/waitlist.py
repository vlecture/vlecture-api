from pydantic import BaseModel, EmailStr

class WaitlistSchema(BaseModel):
    email: EmailStr
