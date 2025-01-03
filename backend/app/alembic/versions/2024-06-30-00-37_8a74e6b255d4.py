"""empty message

Revision ID: 8a74e6b255d4
Revises: ccbe79fdc9aa
Create Date: 2024-06-30 00:37:02.688417

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = '8a74e6b255d4'
down_revision = 'ccbe79fdc9aa'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") 
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Payment',
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('payment_key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('payment_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('order_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('detail', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('artist_goods_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('company_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('artist_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['artist_goods_id'], ['ArtistGoods.id'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Payment_id'), 'Payment', ['id'], unique=False)
    op.add_column('ArtistGoodsDeal', sa.Column('payment_id', sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.create_foreign_key(None, 'ArtistGoodsDeal', 'Payment', ['payment_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ArtistGoodsDeal', type_='foreignkey')
    op.drop_column('ArtistGoodsDeal', 'payment_id')
    op.drop_index(op.f('ix_Payment_id'), table_name='Payment')
    op.drop_table('Payment')
    # ### end Alembic commands ###