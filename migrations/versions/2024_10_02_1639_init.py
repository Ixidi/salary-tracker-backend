"""init

Revision ID: 7d83f8424513
Revises: 
Create Date: 2024-10-02 16:39:15.848601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '7d83f8424513'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('sheets',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('owner_user_uuid', sa.Uuid(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['owner_user_uuid'], ['users.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('user_external_accounts',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('provider', sa.Enum('GOOGLE', name='authprovider'), nullable=False),
    sa.Column('user_uuid', sa.Uuid(), nullable=False),
    sa.Column('external_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ),
    sa.PrimaryKeyConstraint('provider', 'user_uuid')
    )
    op.create_table('user_refresh_tokens',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('user_uuid', sa.Uuid(), nullable=False),
    sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_agent', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ),
    sa.PrimaryKeyConstraint('user_uuid', 'token')
    )
    op.create_table('sheet_rate_tables',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('sheet_uuid', sa.Uuid(), nullable=False),
    sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
    sa.Column('valid_to', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['sheet_uuid'], ['sheets.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('sheet_records',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('sheet_uuid', sa.Uuid(), nullable=False),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.Column('group_size', sa.Integer(), nullable=False),
    sa.Column('group_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('happened_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('additional_info', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['sheet_uuid'], ['sheets.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('sheet_rate_table_durations',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rate_table_uuid', sa.Uuid(), nullable=False),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.ForeignKeyConstraint(['rate_table_uuid'], ['sheet_rate_tables.uuid'], ),
    sa.PrimaryKeyConstraint('duration')
    )
    op.create_table('sheet_rate_table_group_sizes',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rate_table_uuid', sa.Uuid(), nullable=False),
    sa.Column('group_size', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['rate_table_uuid'], ['sheet_rate_tables.uuid'], ),
    sa.PrimaryKeyConstraint('group_size')
    )
    op.create_table('sheet_rate_table_rates',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rate_table_uuid', sa.Uuid(), nullable=False),
    sa.Column('group_size', sa.Integer(), nullable=False),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.Column('rate', sa.Numeric(), nullable=False),
    sa.ForeignKeyConstraint(['rate_table_uuid'], ['sheet_rate_tables.uuid'], ),
    sa.PrimaryKeyConstraint('rate_table_uuid', 'group_size', 'duration')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sheet_rate_table_rates')
    op.drop_table('sheet_rate_table_group_sizes')
    op.drop_table('sheet_rate_table_durations')
    op.drop_table('sheet_records')
    op.drop_table('sheet_rate_tables')
    op.drop_table('user_refresh_tokens')
    op.drop_table('user_external_accounts')
    op.drop_table('sheets')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
