"""Added Language Table

Revision ID: 4fa90183f148
Revises: 4d8b659dd9ff
Create Date: 2020-09-21 14:40:29.786285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fa90183f148'
down_revision = '4d8b659dd9ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('languages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('en_name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_languages_code'), 'languages', ['code'], unique=True)
    op.drop_index('ix_jobs_input', table_name='jobs')
    op.drop_index('ix_jobs_output', table_name='jobs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_jobs_output', 'jobs', ['output'], unique=1)
    op.create_index('ix_jobs_input', 'jobs', ['input'], unique=1)
    op.drop_index(op.f('ix_languages_code'), table_name='languages')
    op.drop_table('languages')
    # ### end Alembic commands ###