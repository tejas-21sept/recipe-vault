"""adding auth api files

Revision ID: 0e72162c7678
Revises: e9b1b21fb0cd
Create Date: 2024-06-08 13:50:11.454272

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0e72162c7678'
down_revision = 'e9b1b21fb0cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('ingredients', sa.Text(), nullable=True),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=120),
               nullable=True)
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
        batch_op.drop_index('email')
        batch_op.drop_index('username')
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))
        batch_op.create_index('username', ['username'], unique=True)
        batch_op.create_index('email', ['email'], unique=True)
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               nullable=False)
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=120),
               nullable=False)
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=64),
               nullable=False)

    op.drop_table('recipe')
    # ### end Alembic commands ###
