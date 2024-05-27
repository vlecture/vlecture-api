from typing import Annotated, List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import UUID4, BeforeValidator
from pydantic import (
    BaseModel,
)

PyObjectId = Annotated[str, BeforeValidator(str)]

class FlashcardUpdateDiffRequest(BaseModel):
    id: UUID4
    new_difficulty: str

class FlashcardSetUpdateLastCompletedRequest(BaseModel):
    id: UUID4
    new_last_completed: datetime

class FlashcardsResponseSchema(BaseModel):
    title: str
    note_id: UUID4
    flashcards: List[dict]

class FlashcardSetsResponseSchema(BaseModel):
    flashcard_sets: List[FlashcardsResponseSchema]

class GenerateFlashcardSetSchema(BaseModel):
    note_id: PyObjectId
    user_id: UUID4
    num_of_flashcards: int
    title: str


class GenerateFlashcardsJSONRequestSchema(BaseModel):
    note_id: PyObjectId
    main: List[dict]
    main_word_count: int
    language: str
    num_of_flashcards: int
    title: str

class GenerateFlashcardsJSONSchema(BaseModel):
    type: str
    front: str
    back: str
    hints: Optional[List[str]]

class GenerateFlashcardResponseJSONSchema(BaseModel):
    note_id: PyObjectId
    set_id: UUID4
    flashcards: List[GenerateFlashcardsJSONSchema]

class FlashcardRequestSchema(BaseModel):
    note_id: PyObjectId
    set_id: UUID4
    type: str
    front: str
    back: str
    hints: Optional[List[str]]