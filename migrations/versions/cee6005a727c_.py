"""empty message

Revision ID: cee6005a727c
Revises: 4c48928ea0b7
Create Date: 2021-03-02 11:52:08.276969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cee6005a727c'
down_revision = '4c48928ea0b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    # ### end Alembic commands ###