"""add content column to Transcriptions table

Revision ID: 9c30378c415f
Revises: 6f702f53e396
Create Date: 2024-03-25 22:06:50.608346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c30378c415f'
down_revision: Union[str, None] = '6f702f53e396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("transcriptions") as alter_table_transcriptions_op:
        alter_table_transcriptions_op.add_column(
            sa.Column("content", sa.TEXT(), nullable=True)
        )


def downgrade() -> None:
    pass
