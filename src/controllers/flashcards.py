from enum import Enum
import http

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests

from src.utils.db import get_db
from src.schemas.base import GenericResponseModel
from src.services.flashcards import FlashcardService
from src.services.users import get_current_user
from src.schemas.flashcards import FlashcardSetsRequestSchema, FlashcardsRequestSchema
from fastapi import HTTPException


class FlashcardsRouterTags(Enum):
    flashcards = "flashcards"


flashcards_router = APIRouter(
    prefix="/v1/flashcards", tags=[FlashcardsRouterTags.flashcards]
)


@flashcards_router.get(
    "/", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel
)
def view_flashcard_sets(
    req: FlashcardSetsRequestSchema, session: Session = Depends(get_db)
):
    service = FlashcardService()

    user_id = req.user_id

    response = service.get_flashcard_sets_by_user(user_id=user_id, session=session)

    try:
        current_user = get_current_user(req, session)
        if current_user.id != user_id:
            raise Exception

        response = service.get_flashcard_sets_by_user(user_id=user_id, session=session)

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
        if current_user.id != user_id:
            raise Exception

        response = service.get_flashcards_by_set(
            set_id=set_id, note_id=note_id, session=session
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


@flashcards_router.delete(
    "/delete/{set_id}",
    status_code=http.HTTPStatus.OK,
    response_model=GenericResponseModel,
)
def delete_flashcard_set(set_id: int, session: Session = Depends(get_db)):
    service = FlashcardService()

    try:
        # Dapatkan id pemilik set
        user_id = service.get_set_owner(set_id)
        current_user = get_current_user(req, session)

        # Pastikan pengguna saat ini adalah pemilik set
        if current_user.id != user_id:
            raise HTTPException(
                status_code=403, detail="Unauthorized to delete this flashcard set."
            )

        # Lakukan penghapusan
        service.delete_flashcard_set(set_id, session)

        # Kirimkan respons berhasil
        return GenericResponseModel(
            status_code=http.HTTPStatus.OK,
            message="Flashcard set successfully deleted.",
            error="",
            data={},
        )
    except HTTPException as e:
        # Kirimkan respons error jika pengguna tidak diizinkan menghapus
        return GenericResponseModel(
            status_code=e.status_code, message="Error", error=e.detail, data={}
        )
    except Exception:
        # Kirimkan respons error untuk kasus lainnya
        return GenericResponseModel(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Error",
            error="An error occurred while trying to delete the flashcard set.",
            data={},
        )
