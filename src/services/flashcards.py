from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import UUID4
from typing import List

from src.models.flashcards import Flashcard, FlashcardSet
from src.utils.db import get_db

class FlashcardService:   

    def get_flashcard_sets_by_user(self, user_id: UUID4, session: Session = Depends(get_db)):
        flashcard_sets = session.query(FlashcardSet).filter(
            FlashcardSet.user_id == user_id,
            FlashcardSet.is_deleted == False
        ).all()

        return self.build_json_flashcard_sets(flashcard_sets)

    def get_flashcards_by_set(self, session: Session, set_id: UUID4, note_id: UUID4):
        flashcards = session.query(Flashcard).filter(
            Flashcard.set_id == set_id,
            Flashcard.note_id == note_id,
            Flashcard.is_deleted == False
        ).all()
        
        return self.build_json_flashcards(flashcards)

    def build_json_flashcard_sets(self, flashcard_sets):
        data = []
        for flashcard_set in flashcard_sets:
            item = {
                "set_id": flashcard_set.set_id,
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