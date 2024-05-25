import json, math
from typing import List
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from openai import OpenAI
from pydantic import UUID4

from starlette.status import HTTP_400_BAD_REQUEST
import datetime

from src.utils.settings import (
    VERY_EASY_DIFF_THRESHOLD,
    EASY_DIFF_THRESHOLD,
    MEDIUM_DIFF_THRESHOLD
)
from src.models.flashcards import Flashcard, FlashcardSet
from src.schemas.flashcards import (
    GenerateFlashcardsJSONRequestSchema,
    GenerateFlashcardSetSchema,
    FlashcardRequestSchema,
    GenerateFlashcardsJSONSchema,
    GenerateFlashcardResponseJSONSchema,
)
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

    def create_flashcard_set(
        self, session: Session, flashcard_set: GenerateFlashcardSetSchema
    ):
        db_flashcard_set = FlashcardSet(**flashcard_set.model_dump())
        session.add(db_flashcard_set)
        session.commit()
        session.refresh(db_flashcard_set)
        return db_flashcard_set.id

    def delete_flashcards_by_set(self, set_id, session: Session):
        flashcard_set = (
            session.query(FlashcardSet).filter(FlashcardSet.id == set_id).first()
        )
        if not flashcard_set:
            raise Exception("flashcard_set set not found")

        session.delete(flashcard_set)
        session.commit()

    def delete_flashcard(self, flashcard_id, session: Session):
        flashcard = (
            session.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
        )
        if not flashcard:
            raise Exception("Flashcard not found")

        session.delete(flashcard)
        session.commit()

    def convert_note_into_flashcard_json(
        self, payload: GenerateFlashcardsJSONRequestSchema
    ) -> GenerateFlashcardsJSONSchema:
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

    def convert_flashcard_json_into_flashcard_schema(
        self,
        set_id: UUID4,
        note_id: UUID4,
        flashcard_json: GenerateFlashcardsJSONSchema,
    ):
        flashcard_schema = FlashcardRequestSchema(
            note_id=note_id,
            set_id=set_id,
            type=flashcard_json.type,
            front=flashcard_json.front,
            back=flashcard_json.back,
            hints=flashcard_json.hints,
        )
        return flashcard_schema

    def create_flashcards(
        self,
        session: Session,
        set_id: UUID4,
        note_id: UUID4,
        flashcard_jsons: List[GenerateFlashcardsJSONSchema],
    ):
        for i, e in enumerate(flashcard_jsons):
            flashcard_json_schema = self.convert_flashcard_json_into_flashcard_schema(
                set_id, note_id, e
            )
            flashcard = Flashcard(**flashcard_json_schema.model_dump())
            session.add(flashcard)
            session.commit()
            session.refresh(flashcard)

        response = GenerateFlashcardResponseJSONSchema(
            note_id=note_id,
            set_id=set_id,
            flashcards=flashcard_jsons,
        )

        return response

    # Flashcard Manipulation and Accessing

    def get_flashcard_sets_by_user(self, user_id: UUID4, session: Session = Depends(get_db)):
        flashcard_sets = session.query(FlashcardSet) \
                        .filter(FlashcardSet.user_id == user_id, FlashcardSet.is_deleted == False) \
                        .all()
        
        return self.build_json_flashcard_sets(flashcard_sets)
    
    def get_recommended_flashcard_sets_by_user(self, user_id: UUID4, session: Session = Depends(get_db)):
        flashcard_sets = session.query(FlashcardSet) \
                        .filter(FlashcardSet.user_id == user_id, FlashcardSet.is_deleted == False) \
                        .all()
        
        flashcard_sets = [x for x in flashcard_sets if self.check_recommended(x.cum_avg_difficulty, x.last_completed)]
        flashcard_sets.sort(key=lambda x: (-x.cum_avg_difficulty, x.last_completed))

        return self.build_json_flashcard_sets(flashcard_sets)
    

    def get_flashcards_by_set(self, session: Session, set_id: UUID4):
        flashcards = session.query(Flashcard).filter(
            Flashcard.set_id == set_id,
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
            flashcard.update_latest_judged_difficulty(new_difficulty, session)

    def update_flashcard_set_last_completed(self, session: Session, set_id: UUID4, new_last_completed: str):
        flashcard_set = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
        ).one()

        if (flashcard_set.is_deleted):
            raise Exception("Flashcard has been deleted")
        else:
            flashcard_set.update_last_completed(new_last_completed, session)


    def build_json_flashcard_sets(self, flashcard_sets):
        data = []
        for flashcard_set in flashcard_sets:
            item = {
                "set_id": str(flashcard_set.id),
                "note_id": str(flashcard_set.note_id),
                "user_id": str(flashcard_set.user_id),
                "title": flashcard_set.title,
                "date_generated": self.format_date(flashcard_set.date_generated),
                "tags": flashcard_set.tags,
                "num_of_flashcards": flashcard_set.num_of_flashcards,
                "is_deleted": flashcard_set.is_deleted,
                "last_accessed": self.format_date(flashcard_set.last_accessed),
                "last_completed": self.format_date(flashcard_set.last_completed),
                "cum_avg_difficulty": flashcard_set.cum_avg_difficulty
            }
            data.append(item)

        return data
    
    def build_json_flashcards(self, flashcards):
        data = []
        for flashcard in flashcards:
            item = {
                "flashcard_id": str(flashcard.id),
                "set_id": str(flashcard.set_id),
                "note_id": str(flashcard.note_id),
                "type": flashcard.type,
                "front": flashcard.front,
                "back": flashcard.back,
                "hints": flashcard.hints,
                "is_deleted": flashcard.is_deleted,
                "num_of_rates": flashcard.num_of_rates,
                "latest_judged_difficulty": flashcard.latest_judged_difficulty,
                "last_accessed": self.format_date(flashcard.last_accessed)
            }
            data.append(item)

        return data
    
    def get_flashcard_by_id(self, session: Session, flashcard_id):
        flashcard = (
            session.query(Flashcard)
            .filter(
                Flashcard.id == flashcard_id,
                Flashcard.is_deleted == False
            )
            .all()
        )

        return flashcard
    
    def get_set_owner(self, set_id, session):
        set_obj = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set_obj.user_id
    
    def get_flashcard_owner(self, flashcard_id, session):
        flashcard = session.query(Flashcard).filter(
            Flashcard.id == flashcard_id,
            Flashcard.is_deleted == False
        ).one()

        return self.get_set_owner(flashcard.set_id, session)
    
    def get_set_title(self, set_id, session):
        set_obj = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set_obj.title

    def get_set_note_id(self, set_id, session):
        set_obj = session.query(FlashcardSet).filter(
            FlashcardSet.id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set_obj.note_id

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

    def format_date(self, date):
        if (date == None):
            return None
        return datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
    
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
            
    def check_recommended(self, avg_cum_difficulty, last_completed):
        if (last_completed == None):
            return True
        if (avg_cum_difficulty <= int(VERY_EASY_DIFF_THRESHOLD)):
            delta =  datetime.timedelta(days=7)
        elif (avg_cum_difficulty <= int(EASY_DIFF_THRESHOLD)):
            delta =  datetime.timedelta(days=3)
        elif (avg_cum_difficulty <= int(MEDIUM_DIFF_THRESHOLD)):
            delta = datetime.timedelta(days=1)
        else:
            delta = datetime.timedelta(hours=1)

        time_to_show = last_completed + delta

        timezone_of_time_to_show = time_to_show.tzinfo
        now_in_timezone = datetime.datetime.now(timezone_of_time_to_show)

        return (time_to_show < now_in_timezone)
