"""empty message

Revision ID: 7a2dcf8ac8bf
Revises: 
Create Date: 2016-11-9 16:24:27.886139

"""

# revision identifiers, used by Alembic.
revision = '7a2dcf8ac8bf'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy as sa

from alembic import op


def upgrade():
    op.create_table(
        'apps',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('project_id', sa.String(255), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.String(255)),
        sa.Column('updated_at', sa.String(255)),
        sa.Column('name', sa.String(255), nullable=False, primary_key=True),
    )


def downgrade():
    op.drop_table('apps')
