"""empty message

Revision ID: bdb810452e49
Revises: 8baee3cd4fed
Create Date: 2024-05-17 06:19:07.521411

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = 'bdb810452e49'
down_revision = '8baee3cd4fed'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") 
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('profile_image_id', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.create_foreign_key(None, 'Artist', 'ImageMedia', ['profile_image_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Artist', type_='foreignkey')
    op.drop_column('Artist', 'profile_image_id')
    # ### end Alembic commands ###