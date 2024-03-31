from enum import Enum
import http

from fastapi import APIRouter, Depends, Body, Request
from sqlalchemy.orm import Session
import requests

from src.utils.db import get_db
from src.schemas.base import GenericResponseModel
from src.services.flashcards import FlashcardService
from src.services.users import get_current_user
from src.models.users import User
from src.schemas.flashcards import (
    FlashcardSetsRequestSchema,
    FlashcardsRequestSchema,
    GenerateFlashcardsJSONRequestSchema,
    GenerateFlashcardSetSchema,
    GenerateFlashcardsJSONSchema
)

class FlashcardsRouterTags(Enum):
    flashcards = "flashcards"

flashcards_router = APIRouter(
    prefix="/v1/flashcards", tags=[FlashcardsRouterTags.flashcards]
)

@flashcards_router.post(
    "/generate", status_code=http.HTTPStatus.OK
)
def generate_flashcards(payload: GenerateFlashcardsJSONRequestSchema = Body(), user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    req_generate_flashcards = GenerateFlashcardsJSONRequestSchema(
        note_id=payload["note_id"],
        main=payload["main"],
        main_word_count=payload["main_word_count"],
        language=payload["language"],
        num_of_flashcards=payload["num_of_flashcards"]
    )

    flashcard_jsons: GenerateFlashcardsJSONSchema = service.convert_note_into_flashcard_json(
        payload=req_generate_flashcards
    )

    req_generate_flashcard_set = GenerateFlashcardSetSchema(
        note_id=payload["note_id"],
        user_id=user["id"],
        num_of_flashcards=payload["num_of_flashcards"],
    )

    set_id = service.create_flashcard_set(
        session=session,
        flashcard_set=req_generate_flashcard_set,
    )
    
    flashcards = service.create_flashcards(
        session=session,
        set_id=set_id,
        note_id=payload["note_id"],
        flashcard_jsons=flashcard_jsons
    )

    return flashcards


@flashcards_router.get(
    "/", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel 
)
def view_flashcard_sets(req: FlashcardSetsRequestSchema, user: User = Depends(get_current_user)):
    service = FlashcardService()

    user_id = req.user_id

    try:
        current_user = get_current_user(req, session)
        if (current_user.id != user_id): 
            raise Exception
        
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
    "/set", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
def view_flashcards(req: FlashcardsRequestSchema, session: Session = Depends(get_db)):
    service = FlashcardService()

    set_id = req.set_id
    note_id = req.note_id

    try:
        user_id = service.get_set_owner(set_id)
        current_user = get_current_user(req, session)
        if (current_user.id != user_id): 
            raise Exception
        
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
            status_code=http.HTTPStatus.UNAUTHORIZED,
            message="Error",
            error="You don't have access to these flashcards or flashcards don't exist.",
            data={},
        )