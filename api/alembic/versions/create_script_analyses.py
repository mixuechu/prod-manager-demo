"""create script analyses table

Revision ID: create_script_analyses
Revises: 
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_script_analyses'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('script_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('character_analysis', sa.JSON(), nullable=True),
        sa.Column('resource_analysis', sa.JSON(), nullable=True),
        sa.Column('scene_analysis', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_script_analyses_id'), 'script_analyses', ['id'], unique=False)
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_script_analyses_id'), table_name='script_analyses')
    op.drop_table('script_analyses')
    # ### end Alembic commands ### 