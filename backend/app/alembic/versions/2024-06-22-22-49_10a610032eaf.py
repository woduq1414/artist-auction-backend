"""empty message

Revision ID: 10a610032eaf
Revises: 1f4869bc8359
Create Date: 2024-06-22 22:49:01.343516

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = '10a610032eaf'
down_revision = '1f4869bc8359'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") 
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Chatting',
    sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('artist_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('company_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('redis_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Chatting_id'), 'Chatting', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Chatting_id'), table_name='Chatting')
    op.drop_table('Chatting')
    # ### end Alembic commands ###