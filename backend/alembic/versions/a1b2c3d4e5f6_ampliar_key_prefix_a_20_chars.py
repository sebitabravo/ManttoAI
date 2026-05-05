"""Ampliar key_prefix de 10 a 20 caracteres para mayor entropía en API Keys.

Revision ID: a1b2c3d4e5f6
Revises: e11486eb753c
Create Date: 2026-05-05

El prefijo de API Key pasó de 8 a 12 caracteres para reducir
el riesgo de colisiones en búsqueda por prefijo bcrypt.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "e11486eb753c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Solo alterar si es MySQL (SQLite no requiere cambio de tamaño)
    dialect = op.get_bind().dialect.name
    if dialect == "mysql":
        op.alter_column(
            "api_keys",
            "key_prefix",
            existing_type=sa.String(10),
            type_=sa.String(20),
            existing_nullable=False,
        )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "mysql":
        op.alter_column(
            "api_keys",
            "key_prefix",
            existing_type=sa.String(20),
            type_=sa.String(10),
            existing_nullable=False,
        )
