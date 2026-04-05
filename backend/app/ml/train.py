"""Entrenamiento del modelo base de ManttoAI."""

from pathlib import Path

import joblib
import pandas as pd
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
) -> Path:
    """Serializa modelo y metadata para reutilización en inferencia."""

    artifact = {
        "model": model,
        "features": FEATURES,
        "target": TARGET_COLUMN,
        "model_params": DEFAULT_MODEL_PARAMS,
    }
    joblib.dump(artifact, output_path)
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
    save_model_artifact(model, output_path=model_path)
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


if __name__ == "__main__":
    output = train_and_save()
    print(f"Modelo entrenado y guardado en: {output}")
