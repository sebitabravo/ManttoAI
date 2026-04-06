"""Deduplica alertas y crea índice único para evitar duplicados activos."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import delete, inspect, select, text


def _bootstrap_backend_imports() -> None:
    """Asegura acceso a backend/ para ejecutar el script desde la raíz."""

    backend_path = Path(__file__).resolve().parents[1] / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))


_bootstrap_backend_imports()

from app.database import SessionLocal, engine, initialize_database_schema  # noqa: E402
from app.models.alerta import Alerta  # noqa: E402

UNIQUE_INDEX_NAME = "uq_alerta_activa_por_equipo_tipo_mensaje"


def dedupe_alertas() -> int:
    """Elimina duplicados manteniendo la alerta más antigua por clave lógica."""

    with SessionLocal() as db:
        alertas = list(db.scalars(select(Alerta).order_by(Alerta.id.asc())))
        seen_keys: set[tuple[int, str, str, bool]] = set()
        duplicate_ids: list[int] = []

        for alerta in alertas:
            dedupe_key = (
                int(alerta.equipo_id),
                str(alerta.tipo),
                str(alerta.mensaje),
                bool(alerta.leida),
            )
            if dedupe_key in seen_keys:
                duplicate_ids.append(int(alerta.id))
                continue

            seen_keys.add(dedupe_key)

        if duplicate_ids:
            db.execute(delete(Alerta).where(Alerta.id.in_(duplicate_ids)))
            db.commit()

        return len(duplicate_ids)


def unique_index_exists() -> bool:
    """Indica si ya existe el índice único esperado para alertas."""

    inspector = inspect(engine)
    indexes = inspector.get_indexes("alertas")
    unique_constraints = inspector.get_unique_constraints("alertas")

    return any(
        index.get("name") == UNIQUE_INDEX_NAME and index.get("unique")
        for index in indexes
    ) or any(
        constraint.get("name") == UNIQUE_INDEX_NAME for constraint in unique_constraints
    )


def create_unique_index() -> bool:
    """Crea índice único si todavía no existe en la base actual."""

    if unique_index_exists():
        return False

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX "
                f"{UNIQUE_INDEX_NAME} ON alertas (equipo_id, tipo, mensaje, leida)"
            )
        )

    return True


def main() -> None:
    """Ejecuta deduplicación e instalación del índice único requerido."""

    initialize_database_schema()
    deleted_count = dedupe_alertas()
    created_index = create_unique_index()

    print("✅ Migración de alertas completada")
    print(f"- Alertas duplicadas eliminadas: {deleted_count}")
    print(f"- Índice único creado: {'sí' if created_index else 'ya existía'}")


if __name__ == "__main__":
    main()
