"""Add rubro to equipos

Revision ID: 9b7c4a21e6f0
Revises: e11486eb753c
Create Date: 2026-05-05 02:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b7c4a21e6f0"
down_revision: Union[str, None] = "e11486eb753c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "equipos",
        sa.Column(
            "rubro",
            sa.String(length=20),
            nullable=False,
            server_default="industrial",
        ),
    )
    op.create_index(op.f("ix_equipos_rubro"), "equipos", ["rubro"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_equipos_rubro"), table_name="equipos")
    op.drop_column("equipos", "rubro")
