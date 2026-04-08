"""Servicios de predicción de riesgo con persistencia en base de datos."""

import logging
from threading import Lock

from collections.abc import Callable

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.ml.train import MODEL_PATH, load_model_artifact_cached, train_and_save_model
from app.models.prediccion import Prediccion
from app.services.alerta_service import (
    create_prediction_failure_alert,
    dispatch_critical_email_notifications,
    dispatch_critical_email_notifications_bg,
    get_active_prediction_failure_alert,
)
from app.services.equipo_service import get_equipo_or_404
from app.services.lectura_service import get_latest_lectura


logger = logging.getLogger(__name__)
_MODEL_BOOTSTRAP_LOCK = Lock()


def load_model_artifact(model_path=MODEL_PATH):
    """Wrapper para permitir monkeypatch flexible en tests y runtime."""

    return load_model_artifact_cached(model_path)


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
            # 422 porque el dato existe pero no es convertible — problema de datos, no del servidor
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Valor inválido para feature '{feature}': {value}",
            ) from exc

    if missing_features:
        # 422 porque la lectura no tiene los campos que el modelo necesita — problema de datos
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Modelo requiere features no disponibles o nulos: {missing_features}"
            ),
        )

    return feature_values


def _load_prediction_artifact_or_503() -> dict[str, object]:
    """Carga artefacto de inferencia o retorna 503 controlado."""

    settings = get_settings()

    try:
        return load_model_artifact(MODEL_PATH)
    except FileNotFoundError as exc:
        if not settings.ml_auto_train_on_missing:
            logger.exception(
                "No se encontró artefacto ML y auto-entrenamiento está deshabilitado"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Modelo de predicción no disponible",
            ) from exc

        logger.warning(
            "Artefacto ML ausente en %s. Se intentará bootstrap automático.",
            MODEL_PATH,
        )
        with _MODEL_BOOTSTRAP_LOCK:
            if not MODEL_PATH.exists():
                try:
                    train_and_save_model(model_path=MODEL_PATH)
                except Exception as train_exc:
                    logger.exception("Falló bootstrap automático del modelo ML")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Modelo de predicción no disponible",
                    ) from train_exc

        try:
            return load_model_artifact(MODEL_PATH)
        except Exception as second_exc:
            logger.exception("No se pudo cargar artefacto ML tras bootstrap automático")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Modelo de predicción no disponible",
            ) from second_exc
    except Exception as exc:
        logger.exception("No se pudo cargar el artefacto de predicción")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo de predicción no disponible",
        ) from exc


def _predict_failure_probability(model, feature_row: list[float]) -> float:
    """Obtiene probabilidad de clase positiva (riesgo/falla)."""

    if not hasattr(model, "predict_proba"):
        if not hasattr(model, "predict"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="El modelo no soporta inferencia válida",
            )

        prediction = model.predict([feature_row])
        if len(prediction) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="El modelo no devolvió predicción válida",
            )

        return 1.0 if int(prediction[0]) == 1 else 0.0

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


def _run_prediction_inference(
    artifact: dict[str, object],
    latest_reading,
) -> tuple[float, str]:
    """Ejecuta inferencia pura sobre la última lectura disponible."""

    model = artifact["model"]
    features = artifact.get("features")
    if not isinstance(features, list) or not features:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Artefacto de modelo inválido: features ausentes",
        )

    feature_row = _build_feature_row_from_lectura(latest_reading, features)
    probability = _predict_failure_probability(model, feature_row)
    return probability, classify_probability(probability)


def _persist_prediction_result(
    db: Session,
    equipo_id: int,
    probability: float,
    classification: str,
    artifact: dict[str, object],
    background_tasks: BackgroundTasks | None = None,
    session_factory: Callable | None = None,
) -> Prediccion:
    """Persiste resultado de inferencia y coordina alerta posterior."""

    prediction = Prediccion(
        equipo_id=equipo_id,
        clasificacion=classification,
        probabilidad=probability,
        modelo_version=_resolve_model_version(artifact),
    )
    db.add(prediction)

    prediction_failure_alert = None
    if classification == "falla":
        prediction_failure_alert = create_prediction_failure_alert(
            db,
            equipo_id=equipo_id,
            probabilidad=probability,
            auto_commit=False,
        )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        if classification != "falla":
            logger.exception("Conflicto de integridad persisitiendo predicción")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de integridad al persistir predicción",
            ) from exc

        if get_active_prediction_failure_alert(db, equipo_id) is None:
            logger.exception("Conflicto de integridad sin alerta activa detectable")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de integridad al persistir predicción",
            ) from exc

        # Reset alert reference: ya existe alerta activa, no creamos duplicado
        prediction_failure_alert = None

        prediction = Prediccion(
            equipo_id=equipo_id,
            clasificacion=classification,
            probabilidad=probability,
            modelo_version=_resolve_model_version(artifact),
        )
        db.add(prediction)

        try:
            db.commit()
        except SQLAlchemyError as retry_exc:
            db.rollback()
            logger.exception(
                "No se pudo persistir la predicción tras deduplicar alerta"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al persistir predicción",
            ) from retry_exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("No se pudo persistir la predicción")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al persistir predicción",
        ) from exc

    db.refresh(prediction)

    logger.info(
        "[PREDICCION] Persistida: equipo_id=%d prediccion_id=%d modelo_version=%s clasificacion=%s probabilidad=%.6f",
        equipo_id,
        prediction.id,
        prediction.modelo_version,
        prediction.clasificacion,
        prediction.probabilidad,
    )

    if prediction_failure_alert is not None:
        db.refresh(prediction_failure_alert)
        if background_tasks:
            background_tasks.add_task(
                dispatch_critical_email_notifications_bg,
                [prediction_failure_alert.id],
                session_factory,
            )
        else:
            dispatch_critical_email_notifications(db, [prediction_failure_alert])

    return prediction


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


def execute_prediction(
    db: Session,
    equipo_id: int,
    background_tasks: BackgroundTasks | None = None,
    session_factory: Callable | None = None,
) -> Prediccion:
    """Ejecuta inferencia real para un equipo y persiste el resultado."""

    get_equipo_or_404(db, equipo_id)
    latest_reading = get_latest_lectura(db, equipo_id)
    logger.info(
        "[PREDICCION] Ejecutando: equipo_id=%d lectura_id=%d",
        equipo_id,
        latest_reading.id,
    )
    artifact = _load_prediction_artifact_or_503()
    probability, classification = _run_prediction_inference(artifact, latest_reading)
    logger.info(
        "[PREDICCION] Resultado: equipo_id=%d probabilidad=%.4f clasificacion=%s",
        equipo_id,
        probability,
        classification,
    )
    return _persist_prediction_result(
        db,
        equipo_id=equipo_id,
        probability=probability,
        classification=classification,
        artifact=artifact,
        background_tasks=background_tasks,
        session_factory=session_factory,
    )
