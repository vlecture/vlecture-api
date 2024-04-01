import json, math
from typing import List
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import OpenAI
from pydantic import UUID4

from starlette.status import HTTP_400_BAD_REQUEST
import datetime

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
                context=self.extract_main_text(payload.main),
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

        return flashcard_sets

    def get_flashcard_set_by_id(self, session: Session, set_id):
        flashcard = (
            session.query(FlashcardSet)
            .filter(
                FlashcardSet.id == set_id,
                Flashcard.is_deleted == False
            )
            .all()
        )

        return flashcard

    def get_flashcards_by_set(self, session: Session, set_id: UUID4):
        flashcards = session.query(Flashcard).filter(
            Flashcard.id == set_id,
            Flashcard.is_deleted == False
        ).all()
        
        return self.build_json_flashcards(flashcards)

    def update_flashcard_difficulty(self, session: Session, flashcard_id: UUID4, new_difficulty: str):
        flashcard = session.query(Flashcard).filter(
            Flashcard.id == flashcard_id,
        ).one()

        if (flashcard.is_deleted):
            raise Exception
        else:
            flashcard.update_latest_judged_difficulty(new_difficulty)

    def get_flashcard_by_id(self, session: Session, flashcard_id):
        flashcard = (
            session.query(Flashcard)
            .filter(
                Flashcard.id == flashcard_id,
                Flashcard.is_deleted == False
            )
            .all()
        )

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
                "front": flashcard.front,
                "back": flashcard.back,
                "is_deleted": flashcard.is_deleted,
                "rated_difficulty": flashcard.rated_difficulty
            }
            data.append(item)

        return data
    
    def get_set_owner(self, set_id, session):
        set = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set.user_id
    
    def get_set_title(self, set_id, session):
        set = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set.title

    def get_set_note_id(self, set_id, session):
        set = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set.note_id

    def rerate_flashcard(
        self, user_id: UUID4, flashcard_id: UUID4, new_rating: str, session: Session 
    ):
        flashcard = self.get_flashcard_by_id(session=session, flashcard_id=flashcard_id)
        flashcard_sets = self.get_flashcard_sets_by_user(user_id=user_id, session=session)

        num_of_rates = flashcard.num_of_rates
        old_flashcard_rating = flashcard.rated_difficulty

        new_flashcard_rating = self.reevaluate_flashcard_rating(new_flashcard_rating=new_rating, old_flashcard_rating=old_flashcard_rating, num_of_rates=num_of_rates)
        flashcard.rated_difficulty = new_flashcard_rating

        self.rerate_flashcard_sets(new_flashcard_rating=new_flashcard_rating, old_flashcard_rating=old_flashcard_rating, flashcard_sets=flashcard_sets, session=session)

        session.commit()

        flashcard = self.get_flashcard_by_id(session=session, flashcard_id=flashcard_id)

        return self.build_json_flashcard(flashcard)

    def rerate_flashcard_sets(
        self, new_flashcard_rating: str, old_flashcard_rating: str, flashcard_sets, session: Session
    ):
        for i, e in enumerate(flashcard_sets):
            flashcard_set = self.get_flashcard_set_by_id(flashcard_sets.id)
            flashcard_set_rating = flashcard_set.avg_difficulty
            num_of_flashcards = flashcard_set.num_of_flashcards

            new_flashcard_set_rating = self.reevaluate_flashcard_set_rating(
                new_flashcard_rating=new_flashcard_rating, 
                old_flashcard_rating=old_flashcard_rating, 
                old_flashcard_set_rating=flashcard_set_rating, 
                num_of_flashcards=num_of_flashcards
            )
            
            flashcard_set.avg_difficulty = new_flashcard_set_rating
            session.commit()

    # Helper Functions

    def extract_main_text(self, main):
        all_text = ""
        for block in main:
            if block["content"]:
                for item in block["content"]:
                    if item["text"]:
                        all_text += item["text"] + " "
        return all_text.strip()

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
                return 4
            case "medium":
                return 3
            case "easy":
                return 2
            case "very_easy":
                return 1

    def reevaluate_flashcard_rating(self, new_flashcard_rating, old_flashcard_rating, num_of_rates):
        new_flashcard_rating = self.rating_enum_to_nominal(new_flashcard_rating)
        old_flashcard_rating = self.rating_enum_to_nominal(old_flashcard_rating)

        rating = ((old_flashcard_rating * num_of_rates) - old_flashcard_rating + new_flashcard_rating) / num_of_rates
        return math.ceil(rating)

    def reevaluate_flashcard_set_rating(self, new_flashcard_rating, old_flashcard_rating, old_flashcard_set_rating, num_of_flashcards):
        new_flashcard_rating = self.rating_enum_to_nominal(new_flashcard_rating)
        old_flashcard_rating = self.rating_enum_to_nominal(old_flashcard_rating)
        old_flashcard_set_rating = self.rating_enum_to_nominal(old_flashcard_set_rating)

        rating = ((old_flashcard_set_rating * num_of_flashcards) - old_flashcard_rating + new_flashcard_rating) / num_of_flashcards
        return math.ceil(rating)