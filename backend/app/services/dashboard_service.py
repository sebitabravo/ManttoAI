"""Servicios agregados para el dashboard."""

from sqlalchemy.orm import Session

from app.services import alerta_service, equipo_service, prediccion_service


def get_dashboard_summary(db: Session) -> dict[str, int | float | str]:
    """Retorna un resumen agregado para la vista principal."""

    equipos = equipo_service.list_equipos(db)
    alertas = alerta_service.list_alertas()
    prediccion = prediccion_service.get_prediction(1)
    return {
        "total_equipos": len(equipos),
        "alertas_activas": len(alertas),
        "equipos_en_riesgo": 1 if prediccion.probabilidad >= 0.5 else 0,
        "ultima_clasificacion": prediccion.clasificacion,
        "probabilidad_falla": prediccion.probabilidad,
    }
