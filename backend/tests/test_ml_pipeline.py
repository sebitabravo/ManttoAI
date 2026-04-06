"""Tests del pipeline ML reproducible."""

from pathlib import Path

import joblib
import pytest

from app.ml.evaluate import evaluate_model
from app.ml.generate_dataset import FEATURES, TARGET_COLUMN, generate_synthetic_dataset
from app.ml import train as train_module
from app.ml.predict import predict_from_record
from app.ml.train import (
    calculate_file_sha256,
    clear_model_artifact_cache,
    load_model_artifact_cached,
    resolve_artifact_checksum_path,
    save_model_artifact,
    train_model,
    verify_artifact_integrity,
)


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
    assert resolve_artifact_checksum_path(saved_path).exists()
    artifact = joblib.load(saved_path)
    assert {"model", "features", "target", "model_params", "metadata"}.issubset(
        artifact.keys()
    )
    assert artifact["features"] == FEATURES
    assert artifact["target"] == TARGET_COLUMN
    assert artifact["metadata"]["artifact_schema_version"] == 2
    assert artifact["metadata"]["model_type"] == "RandomForestClassifier"

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
        "cv_f1_mean",
        "cv_f1_std",
        "cv_precision_mean",
        "cv_recall_mean",
        "cv_folds",
        "train_samples",
        "test_samples",
    }
    assert expected_keys.issubset(metrics.keys())

    assert metrics["train_samples"] + metrics["test_samples"] == 300
    assert metrics["train_samples"] > metrics["test_samples"] > 0

    for metric_name in {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "cv_f1_mean",
        "cv_precision_mean",
        "cv_recall_mean",
    }:
        assert 0.0 <= metrics[metric_name] <= 1.0

    assert metrics["cv_folds"] >= 2


def test_evaluate_model_meets_minimum_f1_requirement():
    """Valida el objetivo académico mínimo de desempeño reproducible."""

    dataset = generate_synthetic_dataset(size=300, seed=42)

    metrics = evaluate_model(dataframe=dataset, test_size=0.2, random_state=42)

    assert metrics["f1"] >= 0.80


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


def test_load_model_artifact_cached_reuses_artifact_until_file_changes(
    tmp_path: Path, monkeypatch
):
    """Valida cache de artefacto ML evitando recargas redundantes desde disco."""

    dataset = generate_synthetic_dataset(size=160, seed=77)
    model = train_model(dataset)
    model_path = tmp_path / "modelo-cache.joblib"
    save_model_artifact(model, output_path=model_path)
    clear_model_artifact_cache()

    original_joblib_load = train_module.joblib.load
    load_calls = {"count": 0}

    def counting_load(path):
        load_calls["count"] += 1
        return original_joblib_load(path)

    monkeypatch.setattr(train_module.joblib, "load", counting_load)

    first_artifact = load_model_artifact_cached(model_path)
    second_artifact = load_model_artifact_cached(model_path)

    assert first_artifact["features"] == second_artifact["features"]
    assert load_calls["count"] == 1

    save_model_artifact(model, output_path=model_path)
    refreshed_artifact = load_model_artifact_cached(model_path)

    assert refreshed_artifact["target"] == TARGET_COLUMN
    assert load_calls["count"] == 2


def test_verify_artifact_integrity_detects_checksum_mismatch(tmp_path: Path):
    """Valida rechazo de artefactos alterados luego de serializarse."""

    dataset = generate_synthetic_dataset(size=120, seed=55)
    model = train_model(dataset)
    model_path = tmp_path / "modelo-integridad.joblib"
    save_model_artifact(model, output_path=model_path, dataset=dataset)

    checksum_before = calculate_file_sha256(model_path)
    model_path.write_bytes(model_path.read_bytes() + b"tampered")

    with pytest.raises(RuntimeError, match="Checksum inválido"):
        verify_artifact_integrity(model_path)

    assert checksum_before != calculate_file_sha256(model_path)
