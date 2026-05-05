"""Servicios agregados para el dashboard."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.prediccion import Prediccion
from app.services import prediccion_service


DashboardEquipoItem = dict[str, int | str | float | None]
DashboardSummaryPayload = dict[str, int | float | str | list[DashboardEquipoItem]]


def _to_float_or_none(value: object) -> float | None:
    """Convierte valores numéricos a float retornando None en casos inválidos."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_dashboard_equipo_items(db: Session) -> list[DashboardEquipoItem]:
    """Construye payload compacto por equipo para polling del dashboard."""

    lecturas_rankeadas = select(
        Lectura.equipo_id.label("equipo_id"),
        Lectura.temperatura.label("ultima_temperatura"),
        func.row_number()
        .over(
            partition_by=Lectura.equipo_id,
            order_by=(Lectura.timestamp.desc(), Lectura.id.desc()),
        )
        .label("ranking"),
    ).subquery()
    ultimas_lecturas = (
        select(
            lecturas_rankeadas.c.equipo_id,
            lecturas_rankeadas.c.ultima_temperatura,
        )
        .where(lecturas_rankeadas.c.ranking == 1)
        .subquery()
    )

    predicciones_rankeadas = select(
        Prediccion.equipo_id.label("equipo_id"),
        Prediccion.probabilidad.label("ultima_probabilidad"),
        # Incluir clasificacion para mostrar el indicador visual en el dashboard
        Prediccion.clasificacion.label("ultima_clasificacion"),
        func.row_number()
        .over(
            partition_by=Prediccion.equipo_id,
            order_by=(Prediccion.created_at.desc(), Prediccion.id.desc()),
        )
        .label("ranking"),
    ).subquery()
    ultimas_predicciones = (
        select(
            predicciones_rankeadas.c.equipo_id,
            predicciones_rankeadas.c.ultima_probabilidad,
            predicciones_rankeadas.c.ultima_clasificacion,
        )
        .where(predicciones_rankeadas.c.ranking == 1)
        .subquery()
    )

    alertas_activas_por_equipo = (
        select(
            Alerta.equipo_id.label("equipo_id"),
            func.count(Alerta.id).label("alertas_activas"),
        )
        .where(Alerta.leida.is_(False))
        .where(Alerta.equipo_id.is_not(None))
        .group_by(Alerta.equipo_id)
        .subquery()
    )

    rows = db.execute(
        select(
            Equipo.id,
            Equipo.nombre,
            Equipo.rubro,
            ultimas_lecturas.c.ultima_temperatura,
            ultimas_predicciones.c.ultima_probabilidad,
            ultimas_predicciones.c.ultima_clasificacion,
            func.coalesce(alertas_activas_por_equipo.c.alertas_activas, 0).label(
                "alertas_activas"
            ),
        )
        .outerjoin(ultimas_lecturas, ultimas_lecturas.c.equipo_id == Equipo.id)
        .outerjoin(ultimas_predicciones, ultimas_predicciones.c.equipo_id == Equipo.id)
        .outerjoin(
            alertas_activas_por_equipo,
            alertas_activas_por_equipo.c.equipo_id == Equipo.id,
        )
        .order_by(Equipo.id)
    ).all()

    equipos: list[DashboardEquipoItem] = []
    for row in rows:
        equipos.append(
            {
                "id": int(row.id),
                "nombre": str(row.nombre),
                "rubro": str(row.rubro or "industrial"),
                "ultima_temperatura": _to_float_or_none(row.ultima_temperatura),
                "ultima_probabilidad": _to_float_or_none(row.ultima_probabilidad),
                # Clasificacion de la última predicción para el indicador visual del frontend
                "ultima_clasificacion": (
                    str(row.ultima_clasificacion) if row.ultima_clasificacion else None
                ),
                "alertas_activas": int(row.alertas_activas or 0),
            }
        )

    return equipos


def get_dashboard_summary(db: Session) -> DashboardSummaryPayload:
    """Retorna un resumen agregado para la vista principal."""

    equipos = _build_dashboard_equipo_items(db)
    prediccion = prediccion_service.get_latest_prediction_global(db)
    if prediccion is not None:
        clasificacion = prediccion.clasificacion
        probabilidad = float(prediccion.probabilidad)
    else:
        clasificacion = "normal"
        probabilidad = 0.0

    alertas_activas = sum(int(equipo["alertas_activas"]) for equipo in equipos)
    equipos_en_riesgo = 0
    for equipo in equipos:
        ultima_probabilidad = equipo["ultima_probabilidad"]
        if ultima_probabilidad is not None and float(ultima_probabilidad) >= 0.5:
            equipos_en_riesgo += 1

    return {
        "total_equipos": len(equipos),
        "alertas_activas": alertas_activas,
        "equipos_en_riesgo": equipos_en_riesgo,
        "ultima_clasificacion": clasificacion,
        "probabilidad_falla": probabilidad,
        "equipos": equipos,
    }
