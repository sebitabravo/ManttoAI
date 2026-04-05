"""Inferencia mínima del modelo ML."""

from pathlib import Path

import joblib

from app.ml.train import FEATURES, MODEL_PATH, save_model, train_model


def load_or_train_model(model_path: Path = MODEL_PATH):
    """Carga el modelo desde disco o entrena uno nuevo si falta."""

    if model_path.exists():
        return joblib.load(model_path)
    model = train_model()
    save_model(model, model_path)
    return model


def predict_from_record(record: dict[str, float]) -> int:
    """Predice riesgo usando un registro con las features esperadas."""

    model = load_or_train_model()
    row = [[record[feature] for feature in FEATURES]]
    return int(model.predict(row)[0])
