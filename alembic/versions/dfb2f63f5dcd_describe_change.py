"""describe change

Revision ID: dfb2f63f5dcd
Revises: 5074b6afff63
Create Date: 2026-03-05 01:22:18.318236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfb2f63f5dcd'
down_revision: Union[str, Sequence[str], None] = '5074b6afff63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
