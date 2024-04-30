import uuid
from pytz import timezone
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    String,
    Integer,
    Enum,
    CheckConstraint,
    TIMESTAMP,
    text,
    Float
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session

from src.utils.db import Base

UTC = timezone("UTC")


def time_now():
    return datetime.now(UTC)

class TypeEnum(Enum):
    __tablename__ = "type_enum"

    question = "Question"
    trueorflase = "TrueOrFalse"
    definition = "Definition"


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    set_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    note_id = Column(String(255), nullable=False)
    type = Column(
        Enum("Question", "TrueOrFalse", "Definition", name="type_enum"),
        nullable=False,
    )
    front = Column(String(300), nullable=False)
    back = Column(String(300), nullable=False)
    hints = Column(ARRAY(String), nullable=True, unique=False, default=[])
    is_deleted = Column(Boolean, default=False)
    num_of_rates=Column(Integer, nullable=False, default=0)
    latest_judged_difficulty = Column(
        Enum("hard", "medium", "easy", "very_easy", name="difficulty_enum"),
        nullable=False,
        default="medium",
    )
    last_accessed = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)

    def update_is_deleted(self, is_deleted, session: Session):
        self.is_deleted = is_deleted
        session.commit()

    def update_latest_judged_difficulty(self, latest_judged_difficulty, session: Session):
        self.latest_judged_difficulty = latest_judged_difficulty
        session.commit()

    def update_last_accessed(self, last_accessed, session: Session):
        self.last_accessed = last_accessed
        session.commit()

class FlashcardSet(Base):
    __tablename__ = "flashcard_sets"

    id = Column(
        UUID(as_uuid=True), 
        nullable=False, 
        primary_key=True, 
        default=uuid.uuid4
    )
    note_id = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(225), nullable=True)
    date_generated = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    tags = Column(ARRAY(String), nullable=True, unique=False)
    num_of_flashcards=Column(Integer, nullable=False, default=0)
    is_deleted = Column(Boolean, nullable=False, default=False)
    last_accessed = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    last_completed = Column(TIMESTAMP(timezone=True), nullable=True)
    cum_avg_difficulty = Column(Float, default=10, nullable=False)

    max_tags = 10
    max_tag_length = 50

    __table_args__ = (
        CheckConstraint(
            text(
                f"array_length(tags, 1) IS NULL OR array_length(tags, 1) <= {max_tag_length}"
            ),
            name="max_tag_length_constraint",
        ),
    )

    def update_is_deleted(self, is_deleted, session: Session):
        self.is_deleted = is_deleted
        session.commit()
    
    def update_last_accessed(self, last_accessed, session: Session):
        self.last_accessed = last_accessed
        session.commit()

    def update_last_completed(self, last_completed, session: Session):
        self.last_completed = last_completed
        session.commit()

    def update_avg_difficulty(self, cum_avg_difficulty, session: Session):
        self.cum_avg_difficulty = cum_avg_difficulty
        session.commit()