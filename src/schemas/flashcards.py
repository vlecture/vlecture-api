from datetime import datetime
from typing import List, Optional

from pydantic import UUID4
from pydantic import (
  BaseModel,
)

class FlashcardsResponseSchema(BaseModel):
    title: str
    note_id: UUID4
    flashcards: List[dict]

class FlashcardSetsResponseSchema(BaseModel):
    flashcard_sets: List[FlashcardsResponseSchema]

class FlashcardUpdateDiffRequest(BaseModel):
    flashcard_id: UUID4
    new_difficulty: str