"""Tests de cobertura para predict.py y utilidades comunes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from app.ml import predict as predict_module
from app.utils.datetime_utils import to_iso, utc_now
from app.utils.validators import is_temperature_valid, is_vibration_valid


class PredictOnlyModel:
    """Mock de modelo con interfaz predict para inferencia."""

    def __init__(self) -> None:
        self.rows: list[list[float]] = []

    def predict(self, rows: list[list[float]]) -> np.ndarray:
        self.rows = rows
        return np.array([1])


def test_load_model_and_features_wraps_loader_errors(monkeypatch, tmp_path):
    """Entrega RuntimeError claro cuando falla carga de artefacto."""

    model_path = tmp_path / "modelo.joblib"

    def failing_loader(_path):
        raise ValueError("artifact corrupt")

    monkeypatch.setattr(predict_module, "load_model_artifact_cached", failing_loader)

    with pytest.raises(RuntimeError, match="No se pudo cargar artefacto ML"):
        predict_module._load_model_and_features(model_path)


def test_load_model_and_features_supports_artifact_dict(monkeypatch, tmp_path):
    """Soporta artefacto nuevo serializado como diccionario."""

    fake_model = PredictOnlyModel()
    model_path = tmp_path / "modelo.joblib"
    monkeypatch.setattr(
        predict_module,
        "load_model_artifact_cached",
        lambda _path: {
            "model": fake_model,
            "features": ["temperatura", "humedad"],
        },
    )

    model, features = predict_module._load_model_and_features(model_path)

    assert model is fake_model
    assert features == ["temperatura", "humedad"]


def test_load_model_and_features_supports_legacy_model(monkeypatch, tmp_path):
    """Si llega objeto modelo (legado), usa FEATURES por defecto."""

    fake_model = PredictOnlyModel()
    model_path = tmp_path / "modelo.joblib"
    monkeypatch.setattr(
        predict_module,
        "load_model_artifact_cached",
        lambda _path: fake_model,
    )

    model, features = predict_module._load_model_and_features(model_path)

    assert model is fake_model
    assert features == predict_module.FEATURES


def test_load_model_and_features_rejects_invalid_artifact(monkeypatch, tmp_path):
    """Falla con mensaje útil cuando artefacto no tiene predict."""

    model_path = tmp_path / "modelo.joblib"
    monkeypatch.setattr(
        predict_module, "load_model_artifact_cached", lambda _path: object()
    )

    with pytest.raises(RuntimeError, match="Artefacto ML no soportado"):
        predict_module._load_model_and_features(model_path)


def test_load_or_train_model_trains_when_file_is_missing(monkeypatch, tmp_path):
    """Si falta artefacto, dispara entrenamiento antes de cargar."""

    model_path = tmp_path / "modelo.joblib"
    train_calls: list[str] = []

    def fake_train_and_save(*, model_path):
        train_calls.append(str(model_path))
        model_path.write_text("artifact", encoding="utf-8")

    monkeypatch.setattr(predict_module, "train_and_save_model", fake_train_and_save)
    monkeypatch.setattr(
        predict_module,
        "_load_model_and_features",
        lambda _path: ("modelo-cargado", predict_module.FEATURES),
    )

    model = predict_module.load_or_train_model(model_path=model_path)

    assert model == "modelo-cargado"
    assert train_calls == [str(model_path)]


def test_load_or_train_model_skips_training_when_file_exists(monkeypatch, tmp_path):
    """No reentrena si el artefacto ya existe en disco."""

    model_path = tmp_path / "modelo.joblib"
    model_path.write_text("artifact", encoding="utf-8")
    train_calls: list[bool] = []

    monkeypatch.setattr(
        predict_module,
        "train_and_save_model",
        lambda **_kwargs: train_calls.append(True),
    )
    monkeypatch.setattr(
        predict_module,
        "_load_model_and_features",
        lambda _path: ("modelo-existente", predict_module.FEATURES),
    )

    model = predict_module.load_or_train_model(model_path=model_path)

    assert model == "modelo-existente"
    assert train_calls == []


def test_predict_from_record_trains_missing_model_and_casts_values(
    monkeypatch, tmp_path
):
    """Convierte features a float y predice correctamente."""

    fake_model = PredictOnlyModel()
    model_path = tmp_path / "modelo.joblib"

    monkeypatch.setattr(predict_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(
        predict_module,
        "train_and_save_model",
        lambda **_kwargs: model_path.write_text("artifact", encoding="utf-8"),
    )
    monkeypatch.setattr(
        predict_module,
        "_load_model_and_features",
        lambda _path: (fake_model, predict_module.FEATURES),
    )

    prediction = predict_module.predict_from_record(
        {
            "temperatura": "55.2",
            "humedad": "66",
            "vib_x": "0.31",
            "vib_y": "0.28",
            "vib_z": "10.12",
        }
    )

    assert prediction == 1
    assert fake_model.rows == [[55.2, 66.0, 0.31, 0.28, 10.12]]


def test_predict_from_record_raises_value_error_for_invalid_values(
    monkeypatch, tmp_path
):
    """Entrega ValueError cuando no puede convertir features numéricas."""

    fake_model = PredictOnlyModel()
    model_path = tmp_path / "modelo.joblib"
    model_path.write_text("artifact", encoding="utf-8")

    monkeypatch.setattr(predict_module, "MODEL_PATH", model_path)
    monkeypatch.setattr(
        predict_module,
        "_load_model_and_features",
        lambda _path: (fake_model, predict_module.FEATURES),
    )

    with pytest.raises(ValueError, match="Valores de features inválidos"):
        predict_module.predict_from_record(
            {
                "temperatura": "nan-text",
                "humedad": 50,
                "vib_x": 0.3,
                "vib_y": 0.2,
                "vib_z": 9.9,
            }
        )


def test_utc_now_returns_aware_datetime_in_utc():
    """La utilidad utc_now devuelve datetime aware en UTC."""

    now = utc_now()

    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)


def test_to_iso_normalizes_timezone_to_utc():
    """to_iso normaliza cualquier tz al formato UTC."""

    chile_tz = timezone(timedelta(hours=-3))
    value = datetime(2026, 4, 7, 20, 0, tzinfo=chile_tz)

    assert to_iso(value) == "2026-04-07T23:00:00+00:00"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-20.0, True),
        (120.0, True),
        (-20.01, False),
        (120.01, False),
    ],
)
def test_is_temperature_valid_respects_boundaries(value: float, expected: bool):
    """Valida rango permitido de temperatura."""

    assert is_temperature_valid(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, True),
        (20.0, True),
        (-0.01, False),
        (20.01, False),
    ],
)
def test_is_vibration_valid_respects_boundaries(value: float, expected: bool):
    """Valida rango permitido de vibración."""

    assert is_vibration_valid(value) is expected
