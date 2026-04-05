"""Evaluación simple del modelo MVP."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

try:
    from app.ml.generate_dataset import (
        DATA_PATH,
        DEFAULT_DATASET_SEED,
        DEFAULT_DATASET_SIZE,
        FEATURES,
        TARGET_COLUMN,
        generate_synthetic_dataset,
        save_dataset,
    )
    from app.ml.train import DEFAULT_MODEL_PARAMS, validate_dataset_schema
except ModuleNotFoundError:  # pragma: no cover - soporte ejecución directa
    from generate_dataset import (  # type: ignore
        DATA_PATH,
        DEFAULT_DATASET_SEED,
        DEFAULT_DATASET_SIZE,
        FEATURES,
        TARGET_COLUMN,
        generate_synthetic_dataset,
        save_dataset,
    )
    from train import DEFAULT_MODEL_PARAMS, validate_dataset_schema  # type: ignore


def load_or_generate_evaluation_dataset(
    dataset_path: Path = DATA_PATH,
    size: int = DEFAULT_DATASET_SIZE,
    seed: int = DEFAULT_DATASET_SEED,
) -> pd.DataFrame:
    """Carga dataset para evaluación o genera uno reproducible."""

    if dataset_path.exists():
        existing_dataset = pd.read_csv(dataset_path)
        validate_dataset_schema(existing_dataset)
        return existing_dataset

    generated = generate_synthetic_dataset(size=size, seed=seed)
    validate_dataset_schema(generated)
    save_dataset(generated, output_path=dataset_path)
    return generated


def evaluate_model(
    dataframe: pd.DataFrame | None = None,
    dataset_path: Path = DATA_PATH,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, float | int]:
    """Evalúa Random Forest con separación honesta train/test."""

    dataset = (
        dataframe
        if dataframe is not None
        else load_or_generate_evaluation_dataset(dataset_path=dataset_path)
    )
    validate_dataset_schema(dataset)

    features_data = dataset[FEATURES]
    target_data = dataset[TARGET_COLUMN]
    stratify_target = target_data if target_data.nunique() > 1 else None

    x_train, x_test, y_train, y_test = train_test_split(
        features_data,
        target_data,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_target,
    )

    model = RandomForestClassifier(**DEFAULT_MODEL_PARAMS)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
    }


if __name__ == "__main__":
    print(evaluate_model())
