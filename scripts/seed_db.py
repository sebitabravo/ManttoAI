"""Puebla datos demo mínimos para el entorno local de ManttoAI."""

from __future__ import annotations

import os
import time
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.exc import OperationalError
from sqlalchemy import select
from sqlalchemy.orm import Session


def _bootstrap_backend_imports() -> None:
    """Asegura que `backend/` esté disponible en el PYTHONPATH."""

    candidates = [
        Path(__file__).resolve().parents[1] / "backend",
        Path("/app"),
        Path.cwd() / "backend",
        Path.cwd(),
    ]

    for candidate in candidates:
        if (candidate / "app").exists():
            backend_path = str(candidate)
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            return

    raise RuntimeError(
        "No se encontró el directorio backend/. "
        "Ejecutá el script desde la raíz del repo o dentro del contenedor backend."
    )


_bootstrap_backend_imports()

from app.database import SessionLocal, initialize_database_schema  # noqa: E402
from app.models.equipo import Equipo  # noqa: E402
from app.models.umbral import Umbral  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.services.auth_service import hash_password  # noqa: E402


@dataclass(frozen=True)
class EquipoSeed:
    """Define un equipo demo para poblar la base de datos."""

    nombre: str
    ubicacion: str
    tipo: str
    estado: str


@dataclass(frozen=True)
class UmbralSeed:
    """Define umbrales base por variable."""

    variable: str
    valor_min: float
    valor_max: float


EQUIPOS_DEMO: tuple[EquipoSeed, ...] = (
    EquipoSeed(
        nombre="Compresor Línea A",
        ubicacion="Planta Norte",
        tipo="Compresor",
        estado="operativo",
    ),
    EquipoSeed(
        nombre="Bomba Hidráulica B",
        ubicacion="Planta Norte",
        tipo="Bomba",
        estado="operativo",
    ),
    EquipoSeed(
        nombre="Motor Ventilación C",
        ubicacion="Planta Sur",
        tipo="Motor",
        estado="operativo",
    ),
)

UMBRALES_BASE: tuple[UmbralSeed, ...] = (
    UmbralSeed(variable="temperatura", valor_min=15.0, valor_max=55.0),
    UmbralSeed(variable="vibracion", valor_min=0.0, valor_max=9.9),
)


def _env_bool(name: str, default: bool = False) -> bool:
    """Lee un booleano desde variables de entorno."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "t", "yes", "y", "si"}


def _assert_safe_seed_environment() -> None:
    """Evita ejecutar el seed fuera de entornos locales sin confirmación."""

    app_env = os.getenv("APP_ENV", "development").strip().lower()
    allow_non_dev = _env_bool("SEED_ALLOW_NON_DEV", default=False)

    if app_env in {"development", "dev", "local"}:
        return

    if allow_non_dev:
        print("⚠️ Seed forzado fuera de desarrollo por SEED_ALLOW_NON_DEV=true")
        return

    raise RuntimeError(
        "Seed bloqueado: APP_ENV no corresponde a desarrollo. "
        "Usá APP_ENV=development o SEED_ALLOW_NON_DEV=true si realmente querés forzar."
    )


def seed_admin_user(db: Session) -> tuple[str, bool]:
    """Crea o actualiza el usuario admin demo."""

    admin_name = os.getenv("SEED_ADMIN_NAME", "Admin ManttoAI")
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@manttoai.local")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin123!")
    reset_admin_password = _env_bool("SEED_RESET_ADMIN_PASSWORD", default=False)

    if admin_password == "Admin123!":
        print(
            "⚠️ Usando contraseña demo por defecto para admin. "
            "Cambiá SEED_ADMIN_PASSWORD en backend/.env para una demo más realista."
        )

    usuario = db.scalars(select(Usuario).where(Usuario.email == admin_email)).first()
    created = usuario is None

    if usuario is None:
        usuario = Usuario(
            nombre=admin_name,
            email=admin_email,
            password_hash=hash_password(admin_password),
            rol="admin",
        )
        db.add(usuario)
    else:
        usuario.nombre = admin_name
        usuario.rol = "admin"

        if reset_admin_password:
            usuario.password_hash = hash_password(admin_password)

    return admin_email, created


def seed_equipos(db: Session) -> tuple[list[Equipo], int, int]:
    """Crea o actualiza equipos demo para la maqueta."""

    equipos: list[Equipo] = []
    created_count = 0
    updated_count = 0

    for equipo_seed in EQUIPOS_DEMO:
        equipo = db.scalars(
            select(Equipo).where(Equipo.nombre == equipo_seed.nombre)
        ).first()

        if equipo is None:
            equipo = Equipo(
                nombre=equipo_seed.nombre,
                ubicacion=equipo_seed.ubicacion,
                tipo=equipo_seed.tipo,
                estado=equipo_seed.estado,
            )
            db.add(equipo)
            db.flush()
            created_count += 1
        else:
            equipo.ubicacion = equipo_seed.ubicacion
            equipo.tipo = equipo_seed.tipo
            equipo.estado = equipo_seed.estado
            updated_count += 1

        equipos.append(equipo)

    return equipos, created_count, updated_count


def seed_umbrales(db: Session, equipos: list[Equipo]) -> tuple[int, int]:
    """Crea o actualiza umbrales base de temperatura y vibración."""

    created_count = 0
    updated_count = 0

    for equipo in equipos:
        for umbral_seed in UMBRALES_BASE:
            umbral = db.scalars(
                select(Umbral)
                .where(Umbral.equipo_id == equipo.id)
                .where(Umbral.variable == umbral_seed.variable)
            ).first()

            if umbral is None:
                umbral = Umbral(
                    equipo_id=equipo.id,
                    variable=umbral_seed.variable,
                    valor_min=umbral_seed.valor_min,
                    valor_max=umbral_seed.valor_max,
                )
                db.add(umbral)
                created_count += 1
            else:
                umbral.valor_min = umbral_seed.valor_min
                umbral.valor_max = umbral_seed.valor_max
                updated_count += 1

    return created_count, updated_count


def initialize_database_with_retry(
    max_attempts: int = 8, delay_seconds: float = 2.0
) -> None:
    """Inicializa esquema con reintentos frente a arranque tardío de MySQL."""

    for attempt in range(1, max_attempts + 1):
        try:
            initialize_database_schema()
            return
        except OperationalError:
            if attempt >= max_attempts:
                raise

            print(
                f"⏳ Base de datos aún no lista para seed (intento {attempt}/{max_attempts}). Reintentando..."
            )
            time.sleep(delay_seconds)


def main() -> None:
    """Ejecuta el seed mínimo requerido para la demo local."""

    _assert_safe_seed_environment()
    initialize_database_with_retry()

    with SessionLocal() as db:
        admin_email, admin_created = seed_admin_user(db)
        equipos, equipos_creados, equipos_actualizados = seed_equipos(db)
        umbrales_creados, umbrales_actualizados = seed_umbrales(db, equipos)

        db.commit()

    print("✅ Seed completado")
    print(
        f"- Usuario admin {'creado' if admin_created else 'actualizado'}: {admin_email}"
    )
    print(
        f"- Equipos: {equipos_creados} creados, {equipos_actualizados} actualizados, "
        f"total objetivo={len(EQUIPOS_DEMO)}"
    )
    print(
        f"- Umbrales: {umbrales_creados} creados, {umbrales_actualizados} actualizados, "
        f"variables por equipo={len(UMBRALES_BASE)}"
    )


if __name__ == "__main__":
    main()
