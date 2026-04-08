"""Puebla datos demo completos para el entorno local de ManttoAI."""

from __future__ import annotations

import os
import random
import time
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
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
from app.models.lectura import Lectura  # noqa: E402
from app.models.alerta import Alerta  # noqa: E402
from app.models.mantencion import Mantencion  # noqa: E402
from app.models.prediccion import Prediccion  # noqa: E402
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

# Semilla para reproducibilidad del demo
SEED_RANDOM = random.Random(42)


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


def seed_tecnico_user(db: Session) -> tuple[str, bool]:
    """Crea o actualiza un usuario técnico para la demo de roles."""

    tecnico_name = os.getenv("SEED_TECNICO_NAME", "Tecnico ManttoAI")
    tecnico_email = os.getenv("SEED_TECNICO_EMAIL", "tecnico@manttoai.local")
    tecnico_password = os.getenv("SEED_TECNICO_PASSWORD", "Tecnico123!")
    reset_tecnico_password = _env_bool("SEED_RESET_TECNICO_PASSWORD", default=False)

    usuario = db.scalars(select(Usuario).where(Usuario.email == tecnico_email)).first()
    created = usuario is None

    if usuario is None:
        usuario = Usuario(
            nombre=tecnico_name,
            email=tecnico_email,
            password_hash=hash_password(tecnico_password),
            rol="tecnico",
        )
        db.add(usuario)
    else:
        usuario.nombre = tecnico_name
        usuario.rol = "tecnico"
        if reset_tecnico_password:
            usuario.password_hash = hash_password(tecnico_password)

    return tecnico_email, created


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


def seed_lecturas_historicas(db: Session, equipos: list[Equipo]) -> tuple[int, int]:
    """Genera 30 días de lecturas históricas por equipo."""

    created_count = 0
    existing_count = 0

    # Verificar si ya existen lecturas
    for equipo in equipos:
        existing = db.scalars(
            select(Lectura).where(Lectura.equipo_id == equipo.id)
        ).first()
        if existing:
            existing_count += 1
            continue

        # Generar 30 días de lecturas (cada 4 horas = 6 lecturas/día = 180 total)
        for day in range(30):
            for hour in range(0, 24, 4):
                timestamp = datetime.now() - timedelta(days=day, hours=hour)

                # Generar valores realistas con algo de variación
                # Equipo 1: Compresor - tiende a temperatura alta
                if "Compresor" in equipo.nombre:
                    temp = SEED_RANDOM.uniform(35, 55)
                    hum = SEED_RANDOM.uniform(30, 50)
                # Equipo 2: Bomba - temperatura media
                elif "Bomba" in equipo.nombre:
                    temp = SEED_RANDOM.uniform(25, 45)
                    hum = SEED_RANDOM.uniform(40, 70)
                # Equipo 3: Motor - temperatura estable
                else:
                    temp = SEED_RANDOM.uniform(20, 40)
                    hum = SEED_RANDOM.uniform(45, 75)

                # Vibración - valores normales pero con algunos picos
                if SEED_RANDOM.random() < 0.05:  # 5% de anomalías
                    vib_x = SEED_RANDOM.uniform(5, 15)
                    vib_y = SEED_RANDOM.uniform(5, 15)
                    vib_z = SEED_RANDOM.uniform(10, 20)
                else:
                    vib_x = SEED_RANDOM.uniform(0, 2)
                    vib_y = SEED_RANDOM.uniform(0, 2)
                    vib_z = SEED_RANDOM.uniform(1, 9)

                lectura = Lectura(
                    equipo_id=equipo.id,
                    temperatura=round(temp, 2),
                    humedad=round(hum, 2),
                    vib_x=round(vib_x, 3),
                    vib_y=round(vib_y, 3),
                    vib_z=round(vib_z, 3),
                    timestamp=timestamp,
                )
                db.add(lectura)
                created_count += 1

    return created_count, existing_count


def seed_predicciones_historicas(db: Session, equipos: list[Equipo]) -> int:
    """Genera predicciones históricas para cada equipo."""

    created_count = 0

    for equipo in equipos:
        # Verificar si ya tiene predicciones
        existing = db.scalars(
            select(Prediccion).where(Prediccion.equipo_id == equipo.id)
        ).first()
        if existing:
            continue

        # Crear última predicción
        if "Compresor" in equipo.nombre:
            clasificacion = "advertencia"
            probabilidad = SEED_RANDOM.uniform(0.6, 0.75)
        elif "Bomba" in equipo.nombre:
            clasificacion = "critico"
            probabilidad = SEED_RANDOM.uniform(0.75, 0.9)
        else:
            clasificacion = "normal"
            probabilidad = SEED_RANDOM.uniform(0.85, 0.95)

        prediccion = Prediccion(
            equipo_id=equipo.id,
            clasificacion=clasificacion,
            probabilidad=round(probabilidad, 3),
            modelo_version="rf-mvp",
            created_at=datetime.now() - timedelta(hours=SEED_RANDOM.randint(1, 48)),
        )
        db.add(prediccion)
        created_count += 1

    return created_count


def seed_alertas_historicas(db: Session, equipos: list[Equipo]) -> tuple[int, int]:
    """Genera alertas de ejemplo para la demo."""

    created_count = 0
    existing_count = 0

    # Definir alertas de ejemplo
    alertas_seed = [
        # Equipo 1: Compresor - algunas alertas de temperatura
        {
            "equipo_nombre": "Compresor Línea A",
            "tipo": "umbral_temperatura",
            "mensaje": "Temperatura elevada detectada: 58°C",
            "nivel": "alto",
        },
        {
            "equipo_nombre": "Compresor Línea A",
            "tipo": "umbral_vibracion",
            "mensaje": "Vibración anormal en eje X: 12.5 m/s²",
            "nivel": "critico",
        },
        # Equipo 2: Bomba - alertas de vibración
        {
            "equipo_nombre": "Bomba Hidráulica B",
            "tipo": "umbral_vibracion",
            "mensaje": "Vibración excesiva detectada: 15.2 m/s²",
            "nivel": "critico",
        },
        {
            "equipo_nombre": "Bomba Hidráulica B",
            "tipo": "prediccion_riesgo",
            "mensaje": "Alto riesgo de falla predicho por ML",
            "nivel": "alto",
        },
        # Equipo 3: Motor - todo normal, una advertencia leve
        {
            "equipo_nombre": "Motor Ventilación C",
            "tipo": "umbral_temperatura",
            "mensaje": "Temperatura ligeramente elevada: 48°C",
            "nivel": "medio",
        },
    ]

    for alerta_data in alertas_seed:
        equipo = db.scalars(
            select(Equipo).where(Equipo.nombre == alerta_data["equipo_nombre"])
        ).first()

        if not equipo:
            continue

        # Verificar si ya existe
        existing = db.scalars(
            select(Alerta)
            .where(Alerta.equipo_id == equipo.id)
            .where(Alerta.tipo == alerta_data["tipo"])
            .where(Alerta.mensaje == alerta_data["mensaje"])
        ).first()

        if existing:
            existing_count += 1
            continue

        # Crear alerta (algunas leídas, otras no)
        is_read = SEED_RANDOM.random() < 0.4  # 40% leídas

        alerta = Alerta(
            equipo_id=equipo.id,
            tipo=alerta_data["tipo"],
            mensaje=alerta_data["mensaje"],
            nivel=alerta_data["nivel"],
            email_enviado=alerta_data["nivel"] in ("alto", "critico"),
            leida=is_read,
            created_at=datetime.now() - timedelta(hours=SEED_RANDOM.randint(1, 72)),
        )
        db.add(alerta)
        created_count += 1

    return created_count, existing_count


def seed_mantenciones_historicas(db: Session, equipos: list[Equipo]) -> tuple[int, int]:
    """Genera registros de mantención para la demo."""

    created_count = 0
    existing_count = 0

    # Definir mantenciones de ejemplo
    mantenciones_seed = [
        # Compresor - varias mantenciones
        {
            "equipo_nombre": "Compresor Línea A",
            "tipo": "preventiva",
            "descripcion": "Cambio de filtros de aire",
            "estado": "completada",
            "dias_atras": 15,
        },
        {
            "equipo_nombre": "Compresor Línea A",
            "tipo": "correctiva",
            "descripcion": "Reemplazo de correas de transmisión",
            "estado": "completada",
            "dias_atras": 45,
        },
        {
            "equipo_nombre": "Compresor Línea A",
            "tipo": "preventiva",
            "descripcion": "Lubricación de rodamientos",
            "estado": "completada",
            "dias_atras": 60,
        },
        # Bomba - recientes
        {
            "equipo_nombre": "Bomba Hidráulica B",
            "tipo": "predictiva",
            "descripcion": "Inspección por anomalía de vibración",
            "estado": "programada",
            "dias_atras": -3,  # Futura
        },
        {
            "equipo_nombre": "Bomba Hidráulica B",
            "tipo": "preventiva",
            "descripcion": "Cambio de aceite hidráulico",
            "estado": "completada",
            "dias_atras": 30,
        },
        # Motor - una pendiente
        {
            "equipo_nombre": "Motor Ventilación C",
            "tipo": "preventiva",
            "descripcion": "Limpieza de aspas y inspección de rodamientos",
            "estado": "programada",
            "dias_atras": -7,  # Futura
        },
        {
            "equipo_nombre": "Motor Ventilación C",
            "tipo": "correctiva",
            "descripcion": "Alineación de eje",
            "estado": "completada",
            "dias_atras": 90,
        },
    ]

    for mant_data in mantenciones_seed:
        equipo = db.scalars(
            select(Equipo).where(Equipo.nombre == mant_data["equipo_nombre"])
        ).first()

        if not equipo:
            continue

        # Verificar si ya existe相似的
        existing = db.scalars(
            select(Mantencion)
            .where(Mantencion.equipo_id == equipo.id)
            .where(Mantencion.descripcion == mant_data["descripcion"])
        ).first()

        if existing:
            existing_count += 1
            continue

        dias = int(mant_data["dias_atras"])
        # Convención: dias_atras > 0 => evento pasado, dias_atras < 0 => evento futuro
        fecha_programada = (
            datetime.now() - timedelta(days=dias)
            if dias > 0
            else datetime.now() + timedelta(days=abs(dias))
        )
        fecha_ejecucion = (
            fecha_programada
            if mant_data["estado"] in {"ejecutada", "completada"}
            else None
        )

        mant = Mantencion(
            equipo_id=equipo.id,
            tipo=mant_data["tipo"],
            descripcion=mant_data["descripcion"],
            fecha_programada=fecha_programada,
            fecha_ejecucion=fecha_ejecucion,
            estado=mant_data["estado"],
            created_at=datetime.now() - timedelta(days=abs(dias) + 5),
        )
        db.add(mant)
        created_count += 1

    return created_count, existing_count


def seed_demo_story(db: Session, equipos: list[Equipo]) -> tuple[int, int, int]:
    """Crea una narrativa de demo: normal → alerta → falla → mantención → normal."""

    if not equipos:
        return 0, 0, 0

    equipo = next((item for item in equipos if "Compresor" in item.nombre), equipos[0])

    story_tag = "[STORY-DEMO]"
    existing_story = db.scalars(
        select(Mantencion)
        .where(Mantencion.equipo_id == equipo.id)
        .where(Mantencion.descripcion.contains(story_tag))
    ).first()
    if existing_story:
        return 0, 0, 0

    base_time = datetime.now() - timedelta(days=2)

    lecturas_story = [
        # Estado inicial normal
        (41.5, 52.0, 0.22, 0.18, 9.68, base_time),
        # Aumento de temperatura/vibración (debería gatillar alerta)
        (59.2, 48.0, 0.78, 0.61, 10.45, base_time + timedelta(hours=6)),
        # Condición de falla crítica
        (63.7, 45.5, 1.10, 0.97, 11.20, base_time + timedelta(hours=12)),
        # Post mantención: vuelve a normal
        (43.0, 53.4, 0.24, 0.21, 9.72, base_time + timedelta(hours=36)),
    ]

    lecturas_creadas = 0
    for temp, hum, vib_x, vib_y, vib_z, timestamp in lecturas_story:
        db.add(
            Lectura(
                equipo_id=equipo.id,
                temperatura=temp,
                humedad=hum,
                vib_x=vib_x,
                vib_y=vib_y,
                vib_z=vib_z,
                timestamp=timestamp,
            )
        )
        lecturas_creadas += 1

    predicciones_story = [
        ("normal", 0.31, base_time + timedelta(hours=1)),
        ("alerta", 0.68, base_time + timedelta(hours=7)),
        ("falla", 0.89, base_time + timedelta(hours=13)),
        ("normal", 0.21, base_time + timedelta(hours=37)),
    ]

    predicciones_creadas = 0
    for clasificacion, probabilidad, created_at in predicciones_story:
        db.add(
            Prediccion(
                equipo_id=equipo.id,
                clasificacion=clasificacion,
                probabilidad=probabilidad,
                modelo_version="rf-demo-story",
                created_at=created_at,
            )
        )
        predicciones_creadas += 1

    mantencion_story = Mantencion(
        equipo_id=equipo.id,
        tipo="correctiva",
        descripcion=(
            f"{story_tag} Intervención correctiva tras alerta crítica de vibración y temperatura"
        ),
        fecha_programada=base_time + timedelta(hours=20),
        fecha_ejecucion=base_time + timedelta(hours=24),
        estado="completada",
        created_at=base_time + timedelta(hours=20),
    )
    db.add(mantencion_story)

    return lecturas_creadas, predicciones_creadas, 1


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
    """Ejecuta el seed completo para la demo local."""

    _assert_safe_seed_environment()
    initialize_database_with_retry()

    with SessionLocal() as db:
        # 1. Usuario admin
        admin_email, admin_created = seed_admin_user(db)
        tecnico_email, tecnico_created = seed_tecnico_user(db)

        # 2. Equipos
        equipos, equipos_creados, equipos_actualizados = seed_equipos(db)

        # 3. Umbrales
        umbrales_creados, umbrales_actualizados = seed_umbrales(db, equipos)

        # 4. Lecturas históricas (30 días)
        lecturas_creadas, lecturas_existentes = seed_lecturas_historicas(db, equipos)

        # 5. Predicciones históricas
        predicciones_creadas = seed_predicciones_historicas(db, equipos)

        # 6. Alertas de ejemplo
        alertas_creadas, alertas_existentes = seed_alertas_historicas(db, equipos)

        # 7. Mantenciones históricas
        mantenciones_creadas, mantenciones_existentes = seed_mantenciones_historicas(
            db, equipos
        )

        # 8. Storyline explícita para defensa
        story_lecturas, story_predicciones, story_mantenciones = seed_demo_story(
            db, equipos
        )

        db.commit()

    print("✅ Seed completado")
    print(
        f"  Usuario admin: {admin_email} ({'creado' if admin_created else 'actualizado'})"
    )
    print(
        f"  Usuario técnico: {tecnico_email} ({'creado' if tecnico_created else 'actualizado'})"
    )
    print(f"  Equipos: {equipos_creados} creados, {equipos_actualizados} actualizados")
    print(
        f"  Umbrales: {umbrales_creados} creados, {umbrales_actualizados} actualizados"
    )
    print(
        f"  Lecturas históricas: {lecturas_creadas} creadas, {lecturas_existentes} ya existentes"
    )
    print(f"  Predicciones: {predicciones_creadas} creadas")
    print(f"  Alertas: {alertas_creadas} creadas, {alertas_existentes} ya existentes")
    print(
        f"  Mantenciones: {mantenciones_creadas} creadas, {mantenciones_existentes} ya existentes"
    )
    print(
        "  Storyline demo: "
        f"{story_lecturas} lecturas, {story_predicciones} predicciones, {story_mantenciones} mantención"
    )
    print("")
    print("📊 El dashboard ahora tiene datos históricos para la demo.")


if __name__ == "__main__":
    main()
