"""Manually add dex_number column to Pokemon table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic
revision = '8e6ce4136a52'  # You can use a different unique identifier here
down_revision = 'previous_revision_id'  # Replace with your last migration ID
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Check if the column already exists to avoid duplication
    if 'dex_number' not in [col['name'] for col in inspector.get_columns('pokemon')]:
        op.add_column('pokemon', sa.Column('dex_number', sa.Integer(), nullable=False))
        op.create_unique_constraint(None, 'pokemon', ['dex_number'])

def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Only drop the column if it exists
    if 'dex_number' in [col['name'] for col in inspector.get_columns('pokemon')]:
        op.drop_constraint(None, 'pokemon', type_='unique')
        op.drop_column('pokemon', 'dex_number')
