"""DB Migration - Flashcard

Revision ID: eddd5c21f4aa
Revises: 9c30378c415f
Create Date: 2024-03-31 00:41:39.632328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eddd5c21f4aa'
down_revision: Union[str, None] = '9c30378c415f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('flashcard_sets')
    op.drop_table('flashcards')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('flashcards',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('set_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('note_id', sa.VARCHAR(length=24), autoincrement=False, nullable=False),
    sa.Column('type', postgresql.ENUM('Question', 'TrueOrFalse', 'Definition', name='type_enum'), autoincrement=False, nullable=False),
    sa.Column('front', sa.VARCHAR(length=225), autoincrement=False, nullable=False),
    sa.Column('back', sa.VARCHAR(length=225), autoincrement=False, nullable=False),
    sa.Column('hints', sa.ARRAY(sa.String), nullable=True, unique=False), 
    sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('rated_difficulty', postgresql.ENUM('hard', 'medium', 'easy', 'very_easy', name='difficulty_enum'), autoincrement=False, nullable=False),
    sa.Column('num_of_rates', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id', name='flashcards_pkey')
    )
    op.create_table('flashcard_sets',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('note_id', sa.VARCHAR(length=24), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=225), autoincrement=False, nullable=False),
    sa.Column('date_generated', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('tags', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True),
    sa.Column('num_of_flashcards', sa.INTEGER(), nullable=False),
    sa.Column('avg_difficulty', postgresql.ENUM('hard', 'medium', 'easy', 'very_easy', name='difficulty_enum'), autoincrement=False, nullable=False),
    sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.CheckConstraint('array_length(tags, 1) IS NULL OR array_length(tags, 1) <= 50', name='max_tag_length_constraint'),
    sa.PrimaryKeyConstraint('id', name='flashcard_sets_pkey')
    )
    # ### end Alembic commands ###