import uuid
from pytz import timezone
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    LargeBinary,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    Enum,
    DateTime,
    CheckConstraint,
    func,
    TIMESTAMP,
    text,
    Float
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from src.utils.db import Base

UTC = timezone("UTC")
def time_now():
    return datetime.now(UTC)

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(
        UUID(as_uuid=True), 
        nullable=False, 
        primary_key=True, 
        default=uuid.uuid4
    )
    set_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    front = Column(String(300), nullable=False)
    back = Column(String(300), nullable=False)
    is_deleted = Column(Boolean, default=False) 
    latest_judged_difficulty = Column(Enum('very easy', 'easy', 'medium', 'hard', name='difficulty_enum'), nullable=False, default='medium')
    last_accessed = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)

    def update_is_deleted(self, is_deleted):
        self.is_deleted = is_deleted
    
    def update_latest_judged_difficulty(self, latest_judged_difficulty):
        self.latest_judged_difficulty = latest_judged_difficulty

    def update_last_accessed(self, last_accessed):
        self.last_accessed = last_accessed

class FlashcardSet(Base):
    __tablename__ = "flashcard_sets" 

    id = Column(
        UUID(as_uuid=True), 
        nullable=False, 
        primary_key=True, 
        default=uuid.uuid4
    )
    note_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    title = Column(String(225), nullable=False)
    date_generated = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    tags = Column(ARRAY(String), nullable=True, unique=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    last_accessed = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    last_completed = Column(TIMESTAMP(timezone=True), nullable=True)
    avg_diff_score = Column(Float, default=10, nullable=False)

    max_tags = 10  
    max_tag_length = 50 

    __table_args__ = (
        CheckConstraint(
            text(f"array_length(tags, 1) IS NULL OR array_length(tags, 1) <= {max_tag_length}"),
            name='max_tag_length_constraint'
        ),
    )

    # flashcards = relationship("Flashcard", back_populates="flashcard_set")

    def update_is_deleted(self, is_deleted):
        self.is_deleted = is_deleted
    
    def update_last_accessed(self, last_accessed):
        self.last_accessed = last_accessed

    def update_last_completed(self, last_completed):
        self.last_completed = last_completed

    def update_avg_diff_score(self, avg_diff_score):
        self.avg_diff_score = avg_diff_score