from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import UUID4
from typing import List
import datetime

from src.models.flashcards import Flashcard, FlashcardSet
from src.utils.db import get_db

class FlashcardService:   

    def get_flashcard_sets_by_user(self, user_id: UUID4, session: Session = Depends(get_db)):
        flashcard_sets = session.query(FlashcardSet).filter(
            FlashcardSet.user_id == user_id,
            FlashcardSet.is_deleted == False
        ).all()

        return self.build_json_flashcard_sets(flashcard_sets)

    def get_flashcards_by_set(self, session: Session, set_id: UUID4):
        flashcards = session.query(Flashcard).filter(
            Flashcard.set_id == set_id,
            Flashcard.is_deleted == False
        ).all()
        
        return self.build_json_flashcards(flashcards)
    
    def update_flashcard_difficulty(self, session: Session, flashcard_id: UUID4, new_difficulty: str):
        flashcard = session.query(Flashcard).filter(
            Flashcard.flashcard_id == flashcard_id,
        ).one()

        if (flashcard.is_deleted):
            raise Exception
        else:
            flashcard.update_rated_difficulty(new_difficulty)

    def build_json_flashcard_sets(self, flashcard_sets):
        data = []
        for flashcard_set in flashcard_sets:
            formatted_date = datetime.datetime.strftime(
                flashcard_set.date_generated, "%Y-%m-%d %H:%M:%S")
            item = {
                "set_id": flashcard_set.set_id,
                "note_id": flashcard_set.note_id,
                "user_id": flashcard_set.user_id,
                "title": flashcard_set.title,
                "date_generated": formatted_date,
                "tags": flashcard_set.tags,
                "is_deleted": flashcard_set.is_deleted,
            }
            data.append(item)

        return data
    
    def build_json_flashcards(self, flashcards):
        data = []
        for flashcard in flashcards:
            item = {
                "flashcard_id": flashcard.flashcard_id,
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
            FlashcardSet.set_id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set.user_id
    
    def get_set_title(self, set_id, session):
        set = session.query(FlashcardSet).filter(
            FlashcardSet.set_id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set.title

    def get_set_note_id(self, set_id, session):
        set = session.query(FlashcardSet).filter(
            FlashcardSet.set_id == set_id,
            FlashcardSet.is_deleted == False
        ).one()

        return set.note_id