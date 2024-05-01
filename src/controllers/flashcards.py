from enum import Enum
import http

from fastapi import APIRouter, Depends, Body, Request
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
import requests

from src.schemas.base import GenericResponseModel
from src.utils.db import get_db
from src.services.flashcards import FlashcardService
from src.services.users import get_current_user
from src.models.users import User
from src.schemas.flashcards import (
    FlashcardSetsResponseSchema,
    FlashcardsResponseSchema,
    FlashcardUpdateDiffRequest, 
    FlashcardSetUpdateLastCompletedRequest,
    GenerateFlashcardsJSONRequestSchema,
    GenerateFlashcardSetSchema,
    GenerateFlashcardsJSONSchema
)
from src.models.users import User

class FlashcardsRouterTags(Enum):
    flashcards = "flashcards"

flashcards_router = APIRouter(
    prefix="/v1/flashcards", tags=[FlashcardsRouterTags.flashcards]
)

TRY_LOGIN_MSG = "Try logging in to access your flashcards."
ERROR_MSG_FLASHCARDS_404 = "You don't have access to these flashcards or flashcards don't exist."

@flashcards_router.post(
    "/generate", status_code=http.HTTPStatus.OK
)
def generate_flashcards(payload: GenerateFlashcardsJSONRequestSchema = Body(), user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    req_generate_flashcards = GenerateFlashcardsJSONRequestSchema(
        note_id=payload.note_id,
        main=payload.main,
        main_word_count=payload.main_word_count,
        language=payload.language,
        num_of_flashcards=payload.num_of_flashcards
    )

    flashcard_jsons: GenerateFlashcardsJSONSchema = service.convert_note_into_flashcard_json(
        payload=req_generate_flashcards
    )

    req_generate_flashcard_set = GenerateFlashcardSetSchema(
        note_id=payload.note_id,
        user_id=user.id,
        num_of_flashcards=payload.num_of_flashcards,
    )

    set_id = service.create_flashcard_set(
        session=session,
        flashcard_set=req_generate_flashcard_set,
    )
    
    flashcards = service.create_flashcards(
        session=session,
        set_id=set_id,
        note_id=payload.note_id,
        flashcard_jsons=flashcard_jsons
    )

    return flashcards


@flashcards_router.get(
    "", status_code=http.HTTPStatus.OK, response_model=FlashcardSetsResponseSchema  
)
def view_flashcard_sets( user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        response = service.get_flashcard_sets_by_user(
            user_id=user.id,
            session=session,
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
    "/recommended", status_code=http.HTTPStatus.OK, response_model=FlashcardSetsResponseSchema  
)
def view_recommended_flashcard_sets( user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        response = service.get_recommended_flashcard_sets_by_user(
            user_id=user.id,
            session=session,
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
            return JSONResponse(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content=TRY_LOGIN_MSG,
            )
    

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
    except Exception:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content=ERROR_MSG_FLASHCARDS_404,
        )
    
@flashcards_router.post(
    "/set/update-flashcard-diff", status_code=http.HTTPStatus.OK
)
def update_flashcard_difficulty(req: FlashcardUpdateDiffRequest, user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        user_id = service.get_flashcard_owner(req.id, session)

        if user.id != user_id:
            return JSONResponse(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content=TRY_LOGIN_MSG,
            )
        
        service.update_flashcard_difficulty(
            flashcard_id=req.id,
            new_difficulty=req.new_difficulty,
            session=session
        )

        return JSONResponse(
            status_code=http.HTTPStatus.OK,
            content="Successfully updated flashcard difficulty.",
        )

    except Exception:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="You don't have access to this flashcard or flashcard doesn't exist.",
        )
    
@flashcards_router.post(
    "/set/update-flashcard-set-last-completed", status_code=http.HTTPStatus.OK
)
def update_flashcard_last_completed(req: FlashcardSetUpdateLastCompletedRequest, user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        user_id = service.get_set_owner(req.id, session)

        if user.id != user_id:
            return JSONResponse(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                content=TRY_LOGIN_MSG,
            )
        
        service.update_flashcard_set_last_completed(
            set_id=req.id,
            new_last_completed=req.new_last_completed,
            session=session
        )

        return JSONResponse(
                status_code=http.HTTPStatus.OK,
                content="Successfully updated flashcard set last completed timestamp.",
            )

    except Exception:
        return JSONResponse(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            content="You don't have access to this flashcard set or flashcard set doesn't exist.",
        )

@flashcards_router.delete("/{flashcard_id}", status_code=200)
async def delete_flashcard(flashcard_id: str, session: Session = Depends(get_db)):
    flashcard_service = FlashcardService()
    try:
        flashcard_service.delete_flashcard(flashcard_id, session)
        return {"message": "Flashcard deleted successfully"}
    except Exception:
        return GenericResponseModel(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            message="Error",
            error=ERROR_MSG_FLASHCARDS_404,
            data={},
        )


@flashcards_router.delete("/set/{flashcard_set_id}", status_code=200)
async def delete_flashcard_set(
    flashcard_set_id: str, session: Session = Depends(get_db)
):
    flashcard_service = FlashcardService()
    try:
        flashcard_service.delete_flashcards_by_set(flashcard_set_id, session)
        return {"message": "Flashcard set deleted successfully"}
    except Exception:
        return GenericResponseModel(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            message="Error",
            error=ERROR_MSG_FLASHCARDS_404,
            data={},
        )