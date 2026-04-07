"""Entrenamiento del modelo base de ManttoAI."""

import hashlib
import logging
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

import joblib
import pandas as pd
from sklearn import __version__ as sklearn_version
from sklearn.ensemble import RandomForestClassifier

try:
    from app.ml.generate_dataset import (
        DATA_PATH,
        DEFAULT_DATASET_SEED,
        DEFAULT_DATASET_SIZE,
        EXPECTED_COLUMNS,
        FEATURES,
        TARGET_COLUMN,
        generate_synthetic_dataset,
        save_dataset,
    )
except ModuleNotFoundError:  # pragma: no cover - soporte ejecución directa
    from generate_dataset import (  # type: ignore
        DATA_PATH,
        DEFAULT_DATASET_SEED,
        DEFAULT_DATASET_SIZE,
        EXPECTED_COLUMNS,
        FEATURES,
        TARGET_COLUMN,
        generate_synthetic_dataset,
        save_dataset,
    )

MODEL_PATH = Path(__file__).resolve().parent / "modelo.joblib"
DEFAULT_MODEL_PARAMS = {
    "n_estimators": 120,
    "max_depth": 10,
    "min_samples_leaf": 2,
    "random_state": 42,
}
_MODEL_ARTIFACT_CACHE_LOCK = Lock()
_MODEL_ARTIFACT_CACHE: dict[Path, tuple[int, dict[str, object]]] = {}


def resolve_artifact_checksum_path(model_path: Path) -> Path:
    """Retorna path del checksum sidecar para un artefacto ML."""

    return model_path.with_suffix(f"{model_path.suffix}.sha256")


def calculate_file_sha256(file_path: Path) -> str:
    """Calcula hash SHA-256 del archivo indicado."""

    digest = hashlib.sha256()
    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_artifact_checksum(model_path: Path) -> None:
    """Escribe checksum sidecar para verificación de integridad."""

    checksum_path = resolve_artifact_checksum_path(model_path)
    checksum_path.write_text(f"{calculate_file_sha256(model_path)}\n", encoding="utf-8")


def verify_artifact_integrity(model_path: Path) -> None:
    """Valida checksum sidecar del artefacto antes de cargarlo."""

    checksum_path = resolve_artifact_checksum_path(model_path)
    if not checksum_path.exists():
        raise RuntimeError(
            f"Falta checksum de integridad para artefacto ML: {checksum_path}"
        )

    expected_checksum = checksum_path.read_text(encoding="utf-8").strip()
    current_checksum = calculate_file_sha256(model_path)
    if expected_checksum != current_checksum:
        raise RuntimeError(
            f"Checksum inválido para artefacto ML en {model_path}: integridad comprometida"
        )


def validate_dataset_schema(dataframe: pd.DataFrame) -> None:
    """Valida que el dataset tenga columnas requeridas del pipeline."""

    missing_columns = [
        column_name
        for column_name in EXPECTED_COLUMNS
        if column_name not in dataframe.columns
    ]
    if missing_columns:
        raise RuntimeError(
            f"Dataset inválido: faltan columnas obligatorias {missing_columns}"
        )


def load_or_generate_dataset(
    dataset_path: Path = DATA_PATH,
    size: int = DEFAULT_DATASET_SIZE,
    seed: int = DEFAULT_DATASET_SEED,
) -> pd.DataFrame:
    """Carga dataset existente o genera uno reproducible si falta."""

    if dataset_path.exists():
        existing_dataset = pd.read_csv(dataset_path)
        validate_dataset_schema(existing_dataset)
        return existing_dataset

    generated = generate_synthetic_dataset(size=size, seed=seed)
    validate_dataset_schema(generated)
    save_dataset(generated, output_path=dataset_path)
    return generated


def train_model(dataframe: pd.DataFrame | None = None) -> RandomForestClassifier:
    """Entrena Random Forest con features explícitas del MVP."""

    dataset = dataframe if dataframe is not None else generate_synthetic_dataset()
    validate_dataset_schema(dataset)
    model = RandomForestClassifier(**DEFAULT_MODEL_PARAMS)
    model.fit(dataset[FEATURES], dataset[TARGET_COLUMN])
    return model


def save_model_artifact(
    model: RandomForestClassifier,
    output_path: Path = MODEL_PATH,
    dataset: pd.DataFrame | None = None,
    dataset_path: Path | None = None,
) -> Path:
    """Serializa modelo y metadata para reutilización en inferencia."""

    metadata = {
        "artifact_schema_version": 2,
        "training_library": "scikit-learn",
        "sklearn_version": sklearn_version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_type": type(model).__name__,
        "feature_count": len(FEATURES),
        "dataset_path": str(dataset_path) if dataset_path is not None else None,
        "dataset_rows": int(len(dataset)) if dataset is not None else None,
        "target_positive_ratio": (
            float(dataset[TARGET_COLUMN].mean()) if dataset is not None else None
        ),
    }

    artifact = {
        "model": model,
        "features": FEATURES,
        "target": TARGET_COLUMN,
        "model_params": DEFAULT_MODEL_PARAMS,
        "metadata": metadata,
    }
    joblib.dump(artifact, output_path)
    write_artifact_checksum(output_path)
    return output_path


def save_model(model: RandomForestClassifier, output_path: Path = MODEL_PATH) -> Path:
    """Mantiene compatibilidad con nombre legado de serialización."""

    return save_model_artifact(model, output_path)


def train_and_save_model(
    dataset_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
) -> Path:
    """Entrena con dataset reproducible y guarda artefacto reutilizable."""

    dataset = load_or_generate_dataset(dataset_path=dataset_path)
    model = train_model(dataset)
    save_model_artifact(
        model,
        output_path=model_path,
        dataset=dataset,
        dataset_path=dataset_path,
    )
    return model_path


def train_and_save(
    dataset_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
) -> Path:
    """Alias explícito para ejecutar pipeline desde CLI."""

    return train_and_save_model(dataset_path=dataset_path, model_path=model_path)


def load_model_artifact(model_path: Path = MODEL_PATH) -> dict[str, object]:
    """Carga artefacto serializado del modelo entrenado."""

    try:
        verify_artifact_integrity(model_path)
        artifact = joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo cargar artefacto ML desde {model_path}: {exc}"
        ) from exc

    if isinstance(artifact, dict):
        required_keys = {"model", "features", "target", "model_params"}
        if not required_keys.issubset(artifact.keys()):
            raise RuntimeError(
                f"Artefacto ML inválido en {model_path}: faltan llaves {required_keys}"
            )
        return artifact

    if not hasattr(artifact, "predict"):
        raise RuntimeError(
            f"Artefacto ML no soportado en {model_path}: se esperaba dict o modelo sklearn"
        )

    return {
        "model": artifact,
        "features": FEATURES,
        "target": TARGET_COLUMN,
        "model_params": DEFAULT_MODEL_PARAMS,
    }


def load_model_artifact_cached(model_path: Path = MODEL_PATH) -> dict[str, object]:
    """Carga artefacto ML con cache por archivo para evitar I/O repetido."""

    resolved_path = model_path.resolve()
    try:
        current_mtime_ns = resolved_path.stat().st_mtime_ns
    except FileNotFoundError:
        clear_model_artifact_cache(resolved_path)
        raise

    with _MODEL_ARTIFACT_CACHE_LOCK:
        cached_entry = _MODEL_ARTIFACT_CACHE.get(resolved_path)
        if cached_entry and cached_entry[0] == current_mtime_ns:
            return deepcopy(cached_entry[1])

        artifact = load_model_artifact(resolved_path)
        _MODEL_ARTIFACT_CACHE[resolved_path] = (current_mtime_ns, artifact)
        return deepcopy(artifact)


def clear_model_artifact_cache(model_path: Path | None = None) -> None:
    """Limpia cache del artefacto ML global o de un archivo específico."""

    with _MODEL_ARTIFACT_CACHE_LOCK:
        if model_path is None:
            _MODEL_ARTIFACT_CACHE.clear()
            return

        _MODEL_ARTIFACT_CACHE.pop(model_path.resolve(), None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    output = train_and_save()
    logging.info("Modelo entrenado y guardado en: %s", output)
