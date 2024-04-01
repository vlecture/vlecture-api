from enum import Enum
import http

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
import requests

from src.utils.db import get_db
from src.services.flashcards import FlashcardService
from src.services.users import get_current_user
from src.schemas.flashcards import (
    FlashcardSetsResponseSchema,
    FlashcardsResponseSchema,
    FlashcardUpdateDiffRequest 
)
from src.models.users import User

class FlashcardsRouterTags(Enum):
    flashcards = "flashcards"

flashcards_router = APIRouter(
    prefix="/v1/flashcards", tags=[FlashcardsRouterTags.flashcards]
)

@flashcards_router.get(
    "", status_code=http.HTTPStatus.OK, response_model=FlashcardSetsResponseSchema  
)
def view_flashcard_sets(user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    user_id = user.id

    try:
        response = service.get_flashcard_sets_by_user(
            user_id=user_id,
            session=session
        )

        return JSONResponse(
            status_code=http.HTTPStatus.OK,
            content=response
        )
    except Exception:
         return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="Error: You don't have access to these flashcard sets or flashcard sets don't exist.",
        )

@flashcards_router.get(
    "/set/{set_id}", status_code=http.HTTPStatus.OK, response_model=FlashcardsResponseSchema
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

        title = service.get_set_title(set_id, session)
        note_id = service.get_set_note_id(set_id, session)

        response = {
            'title': title,
            'note_id': note_id,
            'flashcards': response
        }
        
        return JSONResponse(
            status_code=http.HTTPStatus.OK,
            content=response,
        )
    except Exception as e:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="You don't have access to these flashcards or flashcards don't exist.",
        )
    
@flashcards_router.post(
    "/set/update_diff", status_code=http.HTTPStatus.OK
)
def update_flashcard_difficulty(req: FlashcardUpdateDiffRequest, user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        user_id = user.id

        if user.id != user_id:
            raise Exception
        
        service.update_flashcard_difficulty(
            id=req.id,
            new_difficulty=req.new_difficulty,
            session=session
        )

        return JSONResponse(
            status_code=http.HTTPStatus.OK,
            content="Successfully updated flashcard difficulty.",
        )

    except Exception as e:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="You don't have access to this flashcard or flashcard doesn't exist.",
        )
