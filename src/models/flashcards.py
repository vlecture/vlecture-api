import uuid
from pytz import timezone
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    String,
    Enum,
    CheckConstraint,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY

from src.utils.db import Base

UTC = timezone("UTC")


def time_now():
    return datetime.now(UTC)


class DifficultyEnum(Enum):
    __tablename__ = "difficulty_enum"

    hard = "hard"
    good = "good"
    easy = "easy"

class TypeEnum(Enum):
    __tablename__ = "type_enum"

    identification = "identificaton"
    trueorflase = "trueorfalse"
    definition = "definition"


class Flashcard(Base):
    __tablename__ = "flashcards"

    flashcard_id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    set_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    type = Column(
        TypeEnum,
        nullable=False,
    )
    front = Column(String(300), nullable=False)
    back = Column(String(300), nullable=False)
    hint = Column(String(225), nullable=False)
    is_deleted = Column(Boolean, default=False)
    rated_difficulty = Column(
        Enum("hard", "good", "easy", name="difficulty_enum"),
        nullable=False,
        default="good",
    )

    def update_is_deleted(self, is_deleted):
        self.is_deleted = is_deleted

    def update_rated_difficulty(self, rated_difficulty):
        self.rated_difficulty = rated_difficulty


class FlashcardSet(Base):
    __tablename__ = "flashcard_sets"

    set_id = Column(
        UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4
    )
    note_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    title = Column(String(225), nullable=False)
    date_generated = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    tags = Column(ARRAY(String), nullable=True, unique=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

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

    # flashcards = relationship("Flashcard", back_populates="flashcard_set")

    def update_is_deleted(self, is_deleted):
        self.is_deleted = is_deleted

    #     self.delete_all_flashcards_in_set(self)

    # def delete_all_flashcards_in_set(self):
    #     for flashcard in self.flashcards:
    #         flashcard.update_is_deleted(True)
