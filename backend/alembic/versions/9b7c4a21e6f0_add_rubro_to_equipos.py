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
    bind = op.get_bind()
    check_name = "ck_equipos_rubro_valido"
    check_exists = any(
        constraint.get("name") == check_name
        for constraint in sa.inspect(bind).get_check_constraints("equipos")
    )

    if check_exists and bind.dialect.name == "sqlite":
        # SQLite recrea la tabla al quitar columnas y no permite conservar un
        # CHECK que referencia la columna eliminada.
        with op.batch_alter_table("equipos", recreate="always") as batch_op:
            batch_op.drop_constraint(check_name, type_="check")
            batch_op.drop_column("rubro")
        return

    if check_exists:
        op.drop_constraint(check_name, "equipos", type_="check")
    op.drop_column("equipos", "rubro")
