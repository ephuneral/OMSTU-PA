"""empty message

Revision ID: 0e4d0b6749ca
Revises: 4c7fd663e5bb
Create Date: 2022-05-22 22:04:04.296176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e4d0b6749ca'
down_revision = '4c7fd663e5bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'package', ['package_id'])
    op.alter_column('users', 'image_file',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'image_file',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.drop_constraint(None, 'package', type_='unique')
    # ### end Alembic commands ###