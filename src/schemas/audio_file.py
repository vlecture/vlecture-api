from typing import List
from pydantic import BaseModel

class AudioFileSchema(BaseModel):
    filename: str
    content_type: str