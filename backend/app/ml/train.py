"""Entrenamiento del modelo base de ManttoAI."""

from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier

from app.ml.generate_dataset import generate_synthetic_dataset

MODEL_PATH = Path(__file__).resolve().parent / "modelo.joblib"
FEATURES = ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"]


def train_model() -> RandomForestClassifier:
    """Entrena un Random Forest mínimo para el scaffold."""

    dataset = generate_synthetic_dataset()
    model = RandomForestClassifier(n_estimators=25, random_state=42)
    model.fit(dataset[FEATURES], dataset["riesgo"])
    return model


def save_model(model: RandomForestClassifier, output_path: Path = MODEL_PATH) -> Path:
    """Serializa el modelo entrenado a disco."""

    joblib.dump(model, output_path)
    return output_path


if __name__ == "__main__":
    save_model(train_model())
