"""empty message

Revision ID: 7a50adf52c21
Revises: 9ab829a52ad5
Create Date: 2019-04-30 21:52:44.696436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a50adf52c21'
down_revision = '9ab829a52ad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('count_likes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'count_likes')
    # ### end Alembic commands ###
