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
        sa.Column('email', sa.VARCHAR(length=225), autoincrement=False, nullable=False),
        sa.Column('first_name', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('middle_name', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('hashed_password', postgresql.BYTEA(), autoincrement=False, nullable=False),
        sa.Column('refresh_token', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('access_token', sa.VARCHAR(length=225), autoincrement=False, nullable=True),
        sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),

        sa.PrimaryKeyConstraint('id', name='pk_user_id'),
        sa.UniqueConstraint('email', name='uq_user_email')
    )

    op.create_table(
        'otps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(225), nullable=False),
        sa.Column('token', sa.String(6), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        
        sa.PrimaryKeyConstraint('id', name='pk_otp_id'),
        sa.UniqueConstraint('email', name='uq_otp_token')
    )
    
    op.create_table(
        'transcriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean, nullable=False),
        
        
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
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

        sa.PrimaryKeyConstraint('id', name='transcription_chunks_pkey'),
    )

    op.create_table(
        'waitlist',
        sa.Column('email'),
        sa.Column('date_waitlist'),
        sa.Column('is_sent'),
        sa.Column('date_sent'),

        sa.PrimaryKeyConstraint('email', name='waitlist_pkey')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###