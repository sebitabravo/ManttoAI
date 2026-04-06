"""Inferencia mínima del modelo ML."""

from pathlib import Path

try:
    from app.ml.train import (
        FEATURES,
        MODEL_PATH,
        load_model_artifact_cached,
        train_and_save_model,
    )
except ModuleNotFoundError:  # pragma: no cover - soporte ejecución directa
    from train import (  # type: ignore
        FEATURES,
        MODEL_PATH,
        load_model_artifact_cached,
        train_and_save_model,
    )


def _load_model_and_features(model_path: Path = MODEL_PATH):
    """Carga artefacto de modelo soportando formato nuevo y legado."""

    try:
        artifact = load_model_artifact_cached(model_path)
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo cargar artefacto ML desde {model_path}: {exc}"
        ) from exc

    if isinstance(artifact, dict) and "model" in artifact:
        return artifact["model"], artifact.get("features", FEATURES)

    if not hasattr(artifact, "predict"):
        raise RuntimeError(
            f"Artefacto ML no soportado en {model_path}: se esperaba dict o modelo sklearn"
        )

    return artifact, FEATURES


def load_or_train_model(model_path: Path = MODEL_PATH):
    """Carga el modelo desde disco o entrena uno nuevo si falta."""

    if not model_path.exists():
        train_and_save_model(model_path=model_path)

    model, _features = _load_model_and_features(model_path)
    return model


def predict_from_record(record: dict[str, float]) -> int:
    """Predice riesgo usando un registro con las features esperadas."""

    missing_features = [feature for feature in FEATURES if feature not in record]
    if missing_features:
        raise KeyError(
            f"Faltan features requeridas para la predicción: {missing_features}"
        )

    if not MODEL_PATH.exists():
        train_and_save_model(model_path=MODEL_PATH)

    model, features = _load_model_and_features(MODEL_PATH)

    try:
        row = [[float(record[feature]) for feature in features]]
    except (TypeError, ValueError) as exc:
        raise ValueError("Valores de features inválidos para predicción") from exc

    return int(model.predict(row)[0])
