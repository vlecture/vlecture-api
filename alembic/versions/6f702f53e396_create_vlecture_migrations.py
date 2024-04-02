"""Create vlecture-api tables

Revision ID: 6f702f53e396
Revises: 
Create Date: 2024-02-26 21:06:21.545718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6f702f53e396'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),

        sa.Column('email', sa.VARCHAR(length=225), autoincrement=False, nullable=False),
        sa.Column('first_name', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('middle_name', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('hashed_password', postgresql.BYTEA(), autoincrement=False, nullable=False),
        sa.Column('refresh_token', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('access_token', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),

        sa.PrimaryKeyConstraint('id', name='pk_user_id'),
        sa.UniqueConstraint('email', name='uq_user_email'),
    )

    op.create_table(
        'otps',
        sa.Column('id', sa.UUID(), nullable=False),

        sa.Column('email', sa.String(225), nullable=False),
        sa.Column('token', sa.String(6), nullable=False),

        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name='pk_otp_id'),
        sa.UniqueConstraint('email', name='uq_otp_token'),
    )
    
    op.create_table(
        'transcriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False),
        
        
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('tags', sa.ARRAY(item_type=sa.String), nullable=True),
        sa.Column('duration', sa.Float(precision=1), nullable=False),

        sa.PrimaryKeyConstraint('id', name='transcriptions_pkey'),
    )

    op.create_table(
        'transcription_chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False),
        
        sa.Column('duration', sa.Float(precision=1), nullable=False),
        sa.Column('is_edited', sa.Boolean, nullable=False),
        sa.Column('transcription_id', sa.UUID(), nullable=False),
        
        sa.Column('start_time', sa.Float(precision=1), nullable=False),
        sa.Column('end_time', sa.Float(precision=1), nullable=False),

        sa.Column('content', sa.String(255), nullable=False),

        sa.PrimaryKeyConstraint('id', name='transcription_chunks_pkey'),
    )

    op.create_table(
        'waitlist',
        sa.Column('email', sa.String(225), nullable=False),
        sa.Column('date_waitlist', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_sent', sa.Boolean(), nullable=False),
        sa.Column('date_sent', sa.TIMESTAMP(timezone=True), nullable=True),

        sa.PrimaryKeyConstraint('email', name='waitlist_pkey')
    )

    op.create_table(
        'flashcards',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('set_id', sa.UUID(), nullable=False),
        sa.Column('note_id', sa.String, nullable=False),
        sa.Column('type', sa.Enum("Question", "TrueOrFalse", "Definition", name="type_enum"), nullable=False,),
        sa.Column('front', sa.String(300), nullable=False),
        sa.Column('back', sa.String(300), nullable=False),
        sa.Column('hints', sa.ARRAY(sa.String), nullable=True, unique=False),
        sa.Column('is_deleted', sa.BOOLEAN(), nullable=False),
        sa.Column('num_of_rates', sa.Integer(), nullable=False),
        sa.Column('latest_judged_difficulty', sa.Enum('very easy', 'easy', 'medium', 'hard', name='difficulty_enum'), nullable=False, default='medium'),
        sa.Column('last_accessed', sa.TIMESTAMP(timezone=True), nullable=False),

        sa.PrimaryKeyConstraint('id', name="flashcards_pkey")
    )

    op.create_table(
        'flashcard_sets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('note_id', sa.String, nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('date_generated', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('tags', sa.ARRAY(sa.String), nullable=True, unique=False), 
        sa.Column('num_of_flashcards', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.BOOLEAN(), nullable=False),
        sa.Column('last_accessed', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('last_completed', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('cum_avg_difficulty', sa.Float(), nullable=False),

        sa.PrimaryKeyConstraint('id', name="flashcard_sets_pkey"),
        sa.CheckConstraint("cardinality(tags) <= 10", name="max_tags_constraint"),
        sa.CheckConstraint("array_length(tags, 1) <= 50", name="max_tag_length_constraint")
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
