"""set default board_size to 9

Revision ID: fd7f9f1bb17f
Revises: d092260084d7
Create Date: 2025-10-04 12:33:17.009746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd7f9f1bb17f'
down_revision = 'd092260084d7'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "games",
        "board_size",
        server_default=sa.text("9")
    )

def downgrade():
    op.alter_column(
        "games",
        "board_size",
        server_default=sa.text("19")
    )

