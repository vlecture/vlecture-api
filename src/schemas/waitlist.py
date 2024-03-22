from pydantic import BaseModel

class WaitlistSchema(BaseModel):
    email: str
