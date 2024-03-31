import json
from typing import List
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import OpenAI
from pydantic import UUID4

from starlette.status import HTTP_400_BAD_REQUEST

from src.models.flashcards import Flashcard, FlashcardSet
from src.schemas.flashcards import GenerateFlashcardsJSONRequestSchema, GenerateFlashcardSetSchema, FlashcardRequestSchema, GenerateFlashcardsJSONSchema
from src.utils.openai import construct_system_flashcard_instructions
from src.utils.db import get_db

from src.utils.settings import (
    OPENAI_API_KEY,
    OPENAI_ORG_ID,
    OPENAI_MODEL_NAME,
)


class FlashcardService:
    MODEL_TEMPERATURE = 0.7

    def __init__(self) -> None:
        # Init OpenAI Client
        self.openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            organization=OPENAI_ORG_ID,
        )

    def get_openai(self):
        return self.openai_client

    # Flashcard Generation

    def create_flashcard_set(self, session: Session, flashcard_set: GenerateFlashcardSetSchema):
        db_flashcard_set = FlashcardSet(**flashcard_set.model_dump())
        session.add(db_flashcard_set)
        session.commit()
        session.refresh(db_flashcard_set)
        return db_flashcard_set.id

    def convert_note_into_flashcard_json(self, payload: GenerateFlashcardsJSONRequestSchema) -> GenerateFlashcardsJSONSchema:
        if self.check_word_count(payload.main_word_count, payload.num_of_flashcards):
            client = self.get_openai()
            SYSTEM_PROMPT = construct_system_flashcard_instructions(
                context=payload.main,
                num_of_flashcards=payload.num_of_flashcards,
                language=payload.language,
            )

            chat_completion = client.chat.completions.create(
                model=OPENAI_MODEL_NAME,
                temperature=self.MODEL_TEMPERATURE,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    }
                ],
            )
            llm_answer = chat_completion.choices[0].message.content
            llm_answer = json.loads(llm_answer)
            answer: List[GenerateFlashcardsJSONSchema] = []
            for i, e in enumerate(llm_answer.get("flashcards")):
                flashcard = GenerateFlashcardsJSONSchema(
                    type=e.get("type"),
                    front=e.get("content").get("Front"),
                    back=e.get("content").get("Back"),
                    hints=e.get("content").get("Hints"),
                )
                answer.append(flashcard)

            return answer

    def convert_flashcard_json_into_flashcard_schema(self, set_id: UUID4, note_id: UUID4, flashcard_json: GenerateFlashcardsJSONSchema):
        flashcard_schema = FlashcardRequestSchema(
            note_id=note_id,
            set_id=set_id,
            type=flashcard_json.type,
            front=flashcard_json.front,
            back=flashcard_json.back,
            hints=flashcard_json.hints,
        )
        return flashcard_schema

    def create_flashcards(self, session: Session, set_id: UUID4, note_id: UUID4, flashcard_jsons: List[GenerateFlashcardsJSONSchema]):
        for i, e in enumerate(flashcard_jsons):
            flashcard_json_schema = self.convert_flashcard_json_into_flashcard_schema(set_id, note_id, e) 
            flashcard = Flashcard(**flashcard_json_schema.model_dump())
            session.add(flashcard)
            session.commit()
            session.refresh(flashcard)
        
        return flashcard_jsons

    # Flashcard Manipulation and Accessing

    def get_flashcard_sets_by_user(
        self, user_id: UUID4, session: Session = Depends(get_db)
    ):
        flashcard_sets = (
            session.query(FlashcardSet)
            .filter(FlashcardSet.user_id == user_id, FlashcardSet.is_deleted == False)
            .all()
        )

        return self.build_json_flashcard_sets(flashcard_sets)

    def get_flashcards_by_set(self, session: Session, set_id: UUID4, note_id: UUID4):
        flashcards = (
            session.query(Flashcard)
            .filter(
                Flashcard.set_id == set_id,
                Flashcard.note_id == note_id,
                Flashcard.is_deleted == False,
            )
            .all()
        )

        return self.build_json_flashcards(flashcards)

    def get_flashcard_by_id(self, session: Session, flashcard_id):
        flashcard = (
            session.query(Flashcard)
            .filter(
                Flashcard.id == flashcard_id,
                Flashcard.is_deleted == False
            )
            .all()
        )

        return self.build_json_flashcard(flashcard)

    def build_json_flashcard_sets(self, flashcard_sets):
        data = []
        for flashcard_set in flashcard_sets:
            item = {
                "set_id": flashcard_set.id,
                "note_id": flashcard_set.note_id,
                "user_id": flashcard_set.user_id,
                "title": flashcard_set.title,
                "date_generated": flashcard_set.date_generated,
                "tags": flashcard_set.tags,
                "avg_difficulty": flashcard_set.avg_difficulty,
                "is_deleted": flashcard_set.is_deleted,
            }
            data.append(item)

        return data

    def build_json_flashcards(self, flashcards):
        data = []
        for flashcard in flashcards:
            item = {
                "flashcard_id": flashcard.id,
                "set_id": flashcard.set_id,
                "note_id": flashcard.note_id,
                "type": flashcard.type,
                "front": flashcard.front,
                "back": flashcard.back,
                "hints": flashcard.hints,
                "is_deleted": flashcard.is_deleted,
                "rated_difficulty": flashcard.rated_difficulty,
            }
            data.append(item)

        return data

    def build_json_flashcard(self, flashcard):
        item = {
            "flashcard_id": flashcard.id,
            "set_id": flashcard.set_id,
            "note_id": flashcard.note_id,
            "type": flashcard.type,
            "front": flashcard.front,
            "back": flashcard.back,
            "hints": flashcard.hints,
            "is_deleted": flashcard.is_deleted,
            "rated_difficulty": flashcard.rated_difficulty,
        }

        return item

    def get_set_owner(self, set_id, session):
        set = (
            session.query(FlashcardSet)
            .filter(FlashcardSet.set_id == set_id, FlashcardSet.is_deleted == False)
            .one()
        )

        return set.user_id

    def rerate_flashcard(
        self, set_id: UUID4, note_id: UUID4, new_rating: str, session: Session 
    ):
        flashcards = self.get_flashcards_by_set(session=session, set_id=set_id, note_id=note_id)
        flashcards.rated_difficulty(new_rating)
        session.commit()

        return self.build_json_flashcards(flashcards)

    def rerate_flashcard_set(
        self, user_id: UUID4, new_rating: str, session: Session
    ):
        flashcard_sets = self.get_flashcard_sets_by_user(user_id=user_id, session=session)
        flashcard_sets.avg_difficulty(new_rating)
        session.commit()

        return self.build_json_flashcard_sets(flashcard_sets)

    # Helper Functions

    def check_word_count(self, word_count, num_of_flashcards):
        if word_count // 50 < num_of_flashcards:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Note too short!"
            )
        else:
            return True

    def rating_enum_to_nominal(self, rating):
        match rating:
            case "hard":
                return 8
            case "medium":
                return 6
            case "easy":
                return 4
            case "very_easy":
                return 2

    def reevaluate_flashcard_set_rating(self, new_flashcard_rating, old_flashcard_rating, flashcard_set_rating, num_of_flashcards):
        new_flashcard_rating = self.rating_enum_to_nominal(new_flashcard_rating)
        old_flashcard_rating = self.rating_enum_to_nominal(old_flashcard_rating)
        flashcard_set_rating = self.rating_enum_to_nominal(flashcard_set_rating)

        return ((flashcard_set_rating * num_of_flashcards) - old_flashcard_rating + new_flashcard_rating) / num_of_flashcards