"""empty message

Revision ID: fa1345721e66
Revises: 513471c63cb1
Create Date: 2024-05-28 12:16:48.981195

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = 'fa1345721e66'
down_revision = '513471c63cb1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") 
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ArtistGoods', sa.Column('start_date', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ArtistGoods', 'start_date')
    # ### end Alembic commands ###