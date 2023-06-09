"""empty message

Revision ID: 94124e79f28d
Revises: 0e4d0b6749ca
Create Date: 2022-05-23 13:01:41.229851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94124e79f28d'
down_revision = '0e4d0b6749ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(length=20), nullable=False))
    op.add_column('users', sa.Column('surname', sa.String(length=20), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'surname')
    op.drop_column('users', 'name')
    # ### end Alembic commands ###
