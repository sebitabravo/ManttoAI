"""Servicios agregados para el dashboard."""

from sqlalchemy.orm import Session

from app.services import alerta_service, equipo_service, prediccion_service


def get_dashboard_summary(db: Session) -> dict[str, int | float | str]:
    """Retorna un resumen agregado para la vista principal."""

    equipos = equipo_service.list_equipos(db)
    alertas = alerta_service.list_alertas(db, solo_no_leidas=True, limite=None)
    prediccion = prediccion_service.get_latest_prediction_global(db)
    if prediccion is not None:
        clasificacion = prediccion.clasificacion
        probabilidad = float(prediccion.probabilidad)
    else:
        clasificacion = "normal"
        probabilidad = 0.0

    return {
        "total_equipos": len(equipos),
        "alertas_activas": len(alertas),
        "equipos_en_riesgo": 1 if probabilidad >= 0.5 else 0,
        "ultima_clasificacion": clasificacion,
        "probabilidad_falla": probabilidad,
    }
