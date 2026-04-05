"""Generación de dataset sintético para el MVP."""

from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"]
TARGET_COLUMN = "riesgo"
EXPECTED_COLUMNS = [*FEATURES, TARGET_COLUMN]
DEFAULT_DATASET_SIZE = 1200
DEFAULT_DATASET_SEED = 42

DATA_PATH = Path(__file__).resolve().parent / "data" / "synthetic_readings.csv"


def generate_synthetic_dataset(
    size: int = DEFAULT_DATASET_SIZE,
    seed: int = DEFAULT_DATASET_SEED,
) -> pd.DataFrame:
    """Genera dataset sintético reproducible para entrenamiento ML."""

    rng = np.random.default_rng(seed)
    temperatura = np.clip(rng.normal(45, 6, size), 20, 95)
    humedad = np.clip(rng.normal(58, 10, size), 10, 100)
    vib_x = np.clip(rng.normal(0.35, 0.12, size), 0.02, 1.8)
    vib_y = np.clip(rng.normal(0.22, 0.08, size), 0.01, 1.6)
    vib_z = np.clip(rng.normal(9.72, 0.45, size), 8.2, 13.0)

    puntaje_riesgo = (
        0.22 * (temperatura - 45)
        + 1.15 * (vib_x - 0.35)
        + 0.95 * (vib_y - 0.22)
        + 0.35 * (vib_z - 9.72)
        + 0.04 * (humedad - 58)
    )
    prob_riesgo = 1.0 / (1.0 + np.exp(-puntaje_riesgo))
    riesgo = (rng.uniform(0, 1, size) < prob_riesgo).astype(int)

    return pd.DataFrame(
        {
            "temperatura": temperatura,
            "humedad": humedad,
            "vib_x": vib_x,
            "vib_y": vib_y,
            "vib_z": vib_z,
            TARGET_COLUMN: riesgo,
        }
    )


def save_dataset(dataframe: pd.DataFrame, output_path: Path = DATA_PATH) -> Path:
    """Guarda el dataset generado en disco."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return output_path


def generate_and_save_dataset(
    size: int = DEFAULT_DATASET_SIZE,
    seed: int = DEFAULT_DATASET_SEED,
    output_path: Path = DATA_PATH,
) -> Path:
    """Genera dataset reproducible y lo persiste en disco."""

    return save_dataset(generate_synthetic_dataset(size=size, seed=seed), output_path)


if __name__ == "__main__":
    saved_path = generate_and_save_dataset()
    print(f"Dataset generado en: {saved_path}")
