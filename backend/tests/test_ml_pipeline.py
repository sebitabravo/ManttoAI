"""Tests del pipeline ML reproducible."""

from pathlib import Path

import joblib

from app.ml.evaluate import evaluate_model
from app.ml.generate_dataset import FEATURES, TARGET_COLUMN, generate_synthetic_dataset
from app.ml.predict import predict_from_record
from app.ml.train import save_model_artifact, train_model


def test_generate_dataset_is_reproducible_with_same_seed():
    """Valida reproducibilidad exacta para misma semilla."""

    dataset_a = generate_synthetic_dataset(size=120, seed=2026)
    dataset_b = generate_synthetic_dataset(size=120, seed=2026)

    assert dataset_a.equals(dataset_b)


def test_generate_dataset_changes_when_seed_changes():
    """Valida que cambiar semilla altere el dataset."""

    dataset_a = generate_synthetic_dataset(size=120, seed=2026)
    dataset_b = generate_synthetic_dataset(size=120, seed=2027)

    assert not dataset_a.equals(dataset_b)


def test_train_model_and_save_artifact_is_reusable(tmp_path: Path):
    """Valida entrenamiento y serialización reutilizable del modelo."""

    dataset = generate_synthetic_dataset(size=200, seed=77)
    model = train_model(dataset)
    model_path = tmp_path / "modelo.joblib"

    saved_path = save_model_artifact(model, output_path=model_path)

    assert saved_path.exists()
    artifact = joblib.load(saved_path)
    assert set(artifact.keys()) == {"model", "features", "target", "model_params"}
    assert artifact["features"] == FEATURES
    assert artifact["target"] == TARGET_COLUMN

    prediction = artifact["model"].predict(dataset[FEATURES].head(1))
    assert int(prediction[0]) in {0, 1}


def test_evaluate_model_reports_honest_metrics_without_leakage():
    """Valida métricas y separación train/test con conteos coherentes."""

    dataset = generate_synthetic_dataset(size=300, seed=11)

    metrics = evaluate_model(dataframe=dataset, test_size=0.2, random_state=42)

    expected_keys = {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "train_samples",
        "test_samples",
    }
    assert expected_keys.issubset(metrics.keys())

    assert metrics["train_samples"] + metrics["test_samples"] == 300
    assert metrics["train_samples"] > metrics["test_samples"] > 0

    for metric_name in {"accuracy", "precision", "recall", "f1"}:
        assert 0.0 <= metrics[metric_name] <= 1.0


def test_evaluate_model_handles_single_class_dataset_without_crashing():
    """Valida que evaluate no falle cuando dataset tiene una sola clase."""

    dataset = generate_synthetic_dataset(size=150, seed=33)
    dataset[TARGET_COLUMN] = 0

    metrics = evaluate_model(dataframe=dataset, test_size=0.2, random_state=42)

    assert metrics["train_samples"] + metrics["test_samples"] == 150
    assert metrics["test_samples"] > 0


def test_predict_from_record_validates_missing_features():
    """Valida error claro cuando faltan features requeridas."""

    invalid_record = {
        "temperatura": 44.0,
        "humedad": 58.0,
        "vib_x": 0.3,
        "vib_y": 0.2,
    }

    try:
        predict_from_record(invalid_record)
        assert False, "Se esperaba KeyError por feature faltante"
    except KeyError as exc:
        assert "vib_z" in str(exc)
