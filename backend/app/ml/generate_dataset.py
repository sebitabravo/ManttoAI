"""Generación de dataset sintético para el MVP."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "synthetic_readings.csv"


def generate_synthetic_dataset(size: int = 120, seed: int = 42) -> pd.DataFrame:
    """Genera un dataset sintético simple para entrenamientos iniciales."""

    rng = np.random.default_rng(seed)
    temperatura = rng.normal(45, 6, size)
    humedad = rng.normal(58, 8, size)
    vib_x = rng.normal(0.35, 0.08, size)
    vib_y = rng.normal(0.22, 0.05, size)
    vib_z = rng.normal(9.72, 0.2, size)
    riesgo = ((temperatura > 50) | (vib_x > 0.45)).astype(int)
    return pd.DataFrame(
        {
            "temperatura": temperatura,
            "humedad": humedad,
            "vib_x": vib_x,
            "vib_y": vib_y,
            "vib_z": vib_z,
            "riesgo": riesgo,
        }
    )


def save_dataset(dataframe: pd.DataFrame, output_path: Path = DATA_PATH) -> Path:
    """Guarda el dataset generado en disco."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return output_path


if __name__ == "__main__":
    save_dataset(generate_synthetic_dataset())
