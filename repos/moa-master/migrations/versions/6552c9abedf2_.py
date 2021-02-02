"""empty message

Revision ID: 6552c9abedf2
Revises: ed752bbbc436
Create Date: 2018-09-30 15:11:25.273469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6552c9abedf2'
down_revision = 'ed752bbbc436'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('instagram_include_link', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'instagram_include_link')
    # ### end Alembic commands ###