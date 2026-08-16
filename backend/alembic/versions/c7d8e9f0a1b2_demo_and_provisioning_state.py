"""Add demo account guard and one-shot provisioning state.

Revision ID: c7d8e9f0a1b2
Revises: 9b7c4a21e6f0, a1b2c3d4e5f6
Create Date: 2026-08-16

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c7d8e9f0a1b2"
down_revision: tuple[str, str] = ("9b7c4a21e6f0", "a1b2c3d4e5f6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Agrega el estado persistente de demo y provisioning."""

    op.add_column(
        "usuarios",
        sa.Column("is_demo", sa.Boolean(), server_default="0", nullable=False),
    )
    op.create_table(
        "provisioning_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("expected_mac", sa.String(length=17), nullable=False),
        sa.Column("organizacion_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti"),
    )
    op.create_index(
        op.f("ix_provisioning_tokens_jti"),
        "provisioning_tokens",
        ["jti"],
        unique=False,
    )


def downgrade() -> None:
    """Revierte el estado de provisioning y la marca de demo."""

    op.drop_index(op.f("ix_provisioning_tokens_jti"), table_name="provisioning_tokens")
    op.drop_table("provisioning_tokens")
    op.drop_column("usuarios", "is_demo")
