"""Added OutputLanguage table and created relationships

Revision ID: 079c23a50de7
Revises: bdc539ce236a
Create Date: 2020-09-21 14:54:33.244032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '079c23a50de7'
down_revision = 'bdc539ce236a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('output_languages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('language_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('output_languages')
    # ### end Alembic commands ###