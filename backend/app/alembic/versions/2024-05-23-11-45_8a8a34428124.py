"""empty message

Revision ID: 8a8a34428124
Revises: 837a2ece4b47
Create Date: 2024-05-23 11:45:01.827414

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = '8a8a34428124'
down_revision = '837a2ece4b47'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") 
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ArtistGoods', sa.Column('max_price', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ArtistGoods', 'max_price')
    # ### end Alembic commands ###