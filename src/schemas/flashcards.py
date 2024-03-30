from uuid import UUID
from typing import List

from pydantic import UUID4
from pydantic import (
    BaseModel,
)


class FlashcardSetsRequestSchema(BaseModel):
    user_id: UUID4


class FlashcardsRequestSchema(BaseModel):
    set_id: UUID4
    note_id: UUID4


class GenerateFlashcardsRequestSchema(BaseModel):
    note_id: UUID4
    main: str
    main_word_count: int
    language: str
    num_of_flashcards: int
