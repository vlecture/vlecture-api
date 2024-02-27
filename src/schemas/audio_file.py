from pydantic import BaseModel

class AudioFileSchema(BaseModel):
    filename: str