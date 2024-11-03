"""Add ownership and lucky columns to ShinyPokemon model

Revision ID: 043db4e40474
Revises: 
Create Date: 2024-11-03 11:52:00.018472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '043db4e40474'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the new columns directly
    op.add_column('shinies', sa.Column('brady_own', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('shinies', sa.Column('brady_lucky', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('shinies', sa.Column('matt_own', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('shinies', sa.Column('matt_lucky', sa.Boolean(), nullable=False, server_default=sa.false()))

    # ### end Alembic commands ###


def downgrade():
    # Remove the columns in case of downgrade
    op.drop_column('shinies', 'brady_own')
    op.drop_column('shinies', 'brady_lucky')
    op.drop_column('shinies', 'matt_own')
    op.drop_column('shinies', 'matt_lucky')

    # ### end Alembic commands ###
