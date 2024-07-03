"""empty message

Revision ID: 7f365b7d2d27
Revises: 925824e58f18
Create Date: 2024-07-03 20:20:22.968350

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = '7f365b7d2d27'
down_revision = '925824e58f18'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") 
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ArtistGoodsDeal', sa.Column('request_file_list', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ArtistGoodsDeal', 'request_file_list')
    # ### end Alembic commands ###