"""Servicios de predicción de riesgo con persistencia en base de datos."""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.train import MODEL_PATH, load_model_artifact
from app.models.prediccion import Prediccion
from app.services.equipo_service import get_equipo_or_404
from app.services.lectura_service import get_latest_lectura


logger = logging.getLogger(__name__)


def classify_probability(probability: float) -> str:
    """Clasifica riesgo de falla según umbrales simples del MVP."""

    if probability >= 0.8:
        return "falla"
    if probability >= 0.5:
        return "alerta"
    return "normal"


def _resolve_model_version(artifact: dict[str, object]) -> str:
    """Construye versión simple del modelo a partir de metadata."""

    model_params = artifact.get("model_params")
    if not isinstance(model_params, dict):
        return "rf-mvp"

    estimators = model_params.get("n_estimators")
    random_state = model_params.get("random_state")
    if estimators is None or random_state is None:
        return "rf-mvp"

    return f"rf-n{estimators}-rs{random_state}"


def _build_feature_row_from_lectura(
    lectura,
    features: list[str],
) -> list[float]:
    """Construye fila de features para inferencia desde la última lectura."""

    missing_features: list[str] = []
    feature_values: list[float] = []

    for feature in features:
        if not hasattr(lectura, feature):
            missing_features.append(feature)
            continue

        value = getattr(lectura, feature)
        if value is None:
            missing_features.append(feature)
            continue

        try:
            feature_values.append(float(value))
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Valor inválido para feature '{feature}': {value}",
            ) from exc

    if missing_features:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Modelo requiere features no disponibles o nulos: {missing_features}"
            ),
        )

    return feature_values


def _predict_failure_probability(model, feature_row: list[float]) -> float:
    """Obtiene probabilidad de clase positiva (riesgo/falla)."""

    probabilities = model.predict_proba([feature_row])[0]
    classes = getattr(model, "classes_", None)
    classes_list = list(classes) if classes is not None else None

    if len(probabilities) == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El modelo no devolvió probabilidades válidas",
        )

    if len(probabilities) == 1:
        try:
            probability = float(probabilities[0])
        except (TypeError, ValueError):
            if classes_list and len(classes_list) == 1:
                class_value = int(classes_list[0])
                probability = 1.0 if class_value == 1 else 0.0
            else:
                probability = 0.0

        return float(max(0.0, min(1.0, round(probability, 6))))

    if len(probabilities) > 2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Modelo de inferencia no binario no soportado",
        )

    positive_index = 1
    if classes_list is not None:
        if len(classes_list) != len(probabilities):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="El modelo devolvió clases/probabilidades inconsistentes",
            )
        if 1 in classes_list:
            positive_index = classes_list.index(1)

    probability = float(probabilities[positive_index])
    return float(max(0.0, min(1.0, round(probability, 6))))


def get_latest_prediction(db: Session, equipo_id: int) -> Prediccion | None:
    """Obtiene la última predicción persistida de un equipo."""

    return db.scalars(
        select(Prediccion)
        .where(Prediccion.equipo_id == equipo_id)
        .order_by(Prediccion.created_at.desc(), Prediccion.id.desc())
        .limit(1)
    ).first()


def get_latest_prediction_global(db: Session) -> Prediccion | None:
    """Obtiene la última predicción persistida considerando todos los equipos."""

    return db.scalars(
        select(Prediccion)
        .order_by(Prediccion.created_at.desc(), Prediccion.id.desc())
        .limit(1)
    ).first()


def get_prediction(db: Session, equipo_id: int) -> Prediccion:
    """Entrega la última predicción persistida para un equipo."""

    prediction = get_latest_prediction(db, equipo_id)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Predicción no encontrada para el equipo",
        )
    return prediction


def execute_prediction(db: Session, equipo_id: int) -> Prediccion:
    """Ejecuta inferencia real para un equipo y persiste el resultado."""

    get_equipo_or_404(db, equipo_id)
    latest_reading = get_latest_lectura(db, equipo_id)

    try:
        artifact = load_model_artifact(MODEL_PATH)
    except Exception as exc:
        logger.exception("No se pudo cargar el artefacto de predicción")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo de predicción no disponible",
        ) from exc

    model = artifact["model"]
    features = artifact.get("features")
    if not isinstance(features, list) or not features:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Artefacto de modelo inválido: features ausentes",
        )

    feature_row = _build_feature_row_from_lectura(latest_reading, features)
    probability = _predict_failure_probability(model, feature_row)
    classification = classify_probability(probability)

    prediction = Prediccion(
        equipo_id=equipo_id,
        clasificacion=classification,
        probabilidad=probability,
        modelo_version=_resolve_model_version(artifact),
    )
    db.add(prediction)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("No se pudo persistir la predicción")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al persistir predicción",
        ) from exc

    db.refresh(prediction)
    return prediction
