from enum import Enum
import http

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests

from src.utils.db import get_db
from src.schemas.base import GenericResponseModel
from src.services.flashcards import FlashcardService
from src.schemas.flashcards import (
    FlashcardSetsRequestSchema,
    FlashcardsRequestSchema   
)

class FlashcardsRouterTags(Enum):
    flashcards = "flashcards"

flashcards_router = APIRouter(
    prefix="/v1/flashcards", tags=[FlashcardsRouterTags.flashcards]
)

@flashcards_router.get(
    "/", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel 
)
def view_flashcard_sets(req: FlashcardSetsRequestSchema, session: Session = Depends(get_db)):
    service = FlashcardService()

    user_id = req.user_id

    response = service.get_flashcard_sets_by_user(
        user_id=user_id,
        session=session
    )

    try:
        response = service.get_flashcard_sets_by_user(
            user_id=user_id,
            session=session
        )

        return GenericResponseModel(
            status_code=http.HTTPStatus.OK,
            message="Succesfully fetched all flashcard sets from current user.",
            error="",
            data=response,
        )
    except Exception:
         return GenericResponseModel(
            status_code=http.HTTPStatus.NOT_FOUND,
            message="Error",
            error="Error fetching flashcard sets.",
            data={},
        )

@flashcards_router.get(
    "/set", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
def view_flashcards(req: FlashcardsRequestSchema, session: Session = Depends(get_db)):
    service = FlashcardService()

    set_id = req.set_id
    note_id = req.note_id

    try:
        response = service.get_flashcards_by_set(
            set_id=set_id,
            note_id=note_id,
            session=session
        )

        return GenericResponseModel(
            status_code=http.HTTPStatus.OK,
            message="Succesfully fetched all flashcards from set.",
            error="",
            data=response,
        )
    except Exception as e:
        return GenericResponseModel(
            status_code=http.HTTPStatus.NOT_FOUND,
            message="Error",
            error="Error fetching flashcards in set.",
            data={},
        )