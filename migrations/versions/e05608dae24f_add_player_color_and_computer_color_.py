"""Add player_color and computer_color with default

Revision ID: e05608dae24f
Revises: 735f09e12634
Create Date: 2025-10-04 15:33:29.995934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e05608dae24f'
down_revision = '2865ec28e2b6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('games', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('player_color', sa.String(length=5), nullable=False, server_default='black')
        )
        batch_op.add_column(
            sa.Column('computer_color', sa.String(length=5), nullable=False, server_default='white')
        )
        batch_op.add_column(
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
        )

def downgrade():
    with op.batch_alter_table('games', schema=None) as batch_op:
        batch_op.drop_column('computer_color')
        batch_op.drop_column('player_color')

