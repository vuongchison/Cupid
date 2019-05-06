"""empty message

Revision ID: a4135de7b1dd
Revises: 6bb6ccbc038f
Create Date: 2019-04-30 15:26:42.164534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4135de7b1dd'
down_revision = '6bb6ccbc038f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=128), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_uuid'), 'images', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_images_uuid'), table_name='images')
    op.drop_table('images')
    # ### end Alembic commands ###
