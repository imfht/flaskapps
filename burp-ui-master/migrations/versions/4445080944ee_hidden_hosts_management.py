"""hidden hosts management

Revision ID: 4445080944ee
Revises: 695dcbd29d4f
Create Date: 2018-10-03 11:47:20.028686

"""

# revision identifiers, used by Alembic.
revision = '4445080944ee'
down_revision = '695dcbd29d4f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hidden',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user', sa.String(length=256), nullable=False),
    sa.Column('client', sa.String(length=4096), nullable=True),
    sa.Column('server', sa.String(length=4096), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hidden')
    # ### end Alembic commands ###