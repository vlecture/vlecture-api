from typing import List, Optional

from pydantic import UUID4
from pydantic import (
    BaseModel,
)


class FlashcardSetsRequestSchema(BaseModel):
    user_id: UUID4


class FlashcardsRequestSchema(BaseModel):
    set_id: UUID4
    note_id: UUID4


class GenerateFlashcardSetSchema(BaseModel):
    note_id: UUID4
    user_id: UUID4


class GenerateFlashcardsJSONRequestSchema(BaseModel):
    note_id: UUID4
    main: str
    main_word_count: int
    language: str
    num_of_flashcards: int

class FlashcardsJSONSchema(BaseModel):
    type: str
    front: str
    back: str
    hints: Optional[List[str]]

class GenerateFlashcardRequestSchema(BaseModel):
    note_id: UUID4
    set_id: UUID4
    type: str
    front: str
    back: str
    hints: Optional[List[str]]