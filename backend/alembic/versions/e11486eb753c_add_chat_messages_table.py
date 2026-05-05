"""Add chat_messages table

Revision ID: e11486eb753c
Revises: 41d35d73683b
Create Date: 2026-04-16 14:44:01.088205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e11486eb753c'
down_revision: Union[str, None] = '41d35d73683b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mensajes_chat',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mensaje_usuario', sa.Text(), nullable=False),
        sa.Column('respuesta_ia', sa.Text(), nullable=False),
        sa.Column('fuente', sa.String(50), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_mensajes_chat_id', 'mensajes_chat', ['id'])


def downgrade() -> None:
    op.drop_index('ix_mensajes_chat_id', table_name='mensajes_chat')
    op.drop_table('mensajes_chat')
