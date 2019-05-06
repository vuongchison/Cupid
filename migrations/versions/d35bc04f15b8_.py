"""empty message

Revision ID: d35bc04f15b8
Revises: 88e82b2a6894
Create Date: 2019-05-04 20:56:34.255669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd35bc04f15b8'
down_revision = '88e82b2a6894'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('distances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user1_id', sa.Integer(), nullable=True),
    sa.Column('user2_id', sa.Integer(), nullable=True),
    sa.Column('distance', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_distances_distance'), 'distances', ['distance'], unique=False)
    op.create_index(op.f('ix_distances_timestamp'), 'distances', ['timestamp'], unique=False)
    op.create_index(op.f('ix_distances_user1_id'), 'distances', ['user1_id'], unique=False)
    op.create_index(op.f('ix_distances_user2_id'), 'distances', ['user2_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_distances_user2_id'), table_name='distances')
    op.drop_index(op.f('ix_distances_user1_id'), table_name='distances')
    op.drop_index(op.f('ix_distances_timestamp'), table_name='distances')
    op.drop_index(op.f('ix_distances_distance'), table_name='distances')
    op.drop_table('distances')
    # ### end Alembic commands ###