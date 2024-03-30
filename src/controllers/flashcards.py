from enum import Enum
import http

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests

from src.utils.db import get_db
from src.schemas.base import GenericResponseModel
from src.services.flashcards import FlashcardService
from src.services.users import get_current_user
from src.schemas.flashcards import (
    FlashcardSetsRequestSchema,
    FlashcardsRequestSchema   
)
from src.models.users import User

class FlashcardsRouterTags(Enum):
    flashcards = "flashcards"

flashcards_router = APIRouter(
    prefix="/v1/flashcards", tags=[FlashcardsRouterTags.flashcards]
)

@flashcards_router.get(
    "", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel 
)
def view_flashcard_sets(user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    user_id = user.id

    try:
        response = service.get_flashcard_sets_by_user(
            user_id=user_id,
            session=session
        )
        
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
            status_code=http.HTTPStatus.UNAUTHORIZED,
            message="Error",
            error="You don't have access to these flashcard sets or flashcard sets don't exist.",
            data={},
        )

@flashcards_router.get(
    "/set/{set_id}", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
def view_flashcards(set_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        user_id = service.get_set_owner(set_id, session)

        if user.id != user_id:
            raise Exception

        response = service.get_flashcards_by_set(
            set_id=set_id,
            session=session
        )

        title = service.get_set_title
        note_id = service.get_set_note_id

        response = [title, note_id] + response

        return GenericResponseModel(
            status_code=http.HTTPStatus.OK,
            message="Succesfully fetched all flashcards from set.",
            error="",
            data=response,
        )
    except Exception as e:
        return GenericResponseModel(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            message="Error",
            error="You don't have access to these flashcards or flashcards don't exist.",
            data={},
        )