#!/usr/bin/env python3
"""Genera evidencia reproducible de métricas ML para defensa."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if Path("/app/app").exists() and "/app" not in sys.path:
    sys.path.insert(0, "/app")

try:
    from app.ml.evaluate import evaluate_model
    from app.ml.generate_dataset import (
        DATA_PATH,
        DEFAULT_DATASET_SEED,
        DEFAULT_DATASET_SIZE,
    )
    from app.ml.train import DEFAULT_MODEL_PARAMS
except ModuleNotFoundError as exc:  # pragma: no cover - ejecución fuera de entorno app
    raise SystemExit(
        "No se pudo importar app.ml.*. Ejecutá este script dentro del contenedor backend "
        "(make ml-report) o con PYTHONPATH apuntando a backend/."
    ) from exc

MIN_ACCURACY = 0.80
MIN_F1 = 0.80


def parse_args() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos para el reporte."""

    parser = argparse.ArgumentParser(
        description="Generar reporte reproducible de métricas ML ManttoAI"
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Directorio de salida para JSON y Markdown (por defecto backend/reports).",
    )
    parser.add_argument(
        "--output-prefix",
        default="ml-evaluation-latest",
        help="Prefijo de archivos de salida (sin extensión).",
    )
    return parser.parse_args()


def resolve_default_output_dir() -> Path:
    """Resuelve directorio de salida tanto en host como en contenedor."""

    if Path("/app/app").exists():
        return Path("/app/reports")

    project_root = Path(__file__).resolve().parents[1]
    return project_root / "backend" / "reports"


def build_report_payload(metrics: dict[str, float | int]) -> dict[str, object]:
    """Construye payload estructurado del reporte de métricas."""

    accuracy = float(metrics["accuracy"])
    f1_score = float(metrics["f1"])
    meets_gate = accuracy >= MIN_ACCURACY and f1_score >= MIN_F1

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "path": str(DATA_PATH),
            "default_size": DEFAULT_DATASET_SIZE,
            "default_seed": DEFAULT_DATASET_SEED,
            "evaluated_samples": int(
                metrics["train_samples"] + metrics["test_samples"]
            ),
        },
        "model": {
            "type": "RandomForestClassifier",
            "params": DEFAULT_MODEL_PARAMS,
        },
        "academic_gate": {
            "min_accuracy": MIN_ACCURACY,
            "min_f1": MIN_F1,
            "passed": meets_gate,
        },
        "metrics": {
            "accuracy": accuracy,
            "precision": float(metrics["precision"]),
            "recall": float(metrics["recall"]),
            "f1": f1_score,
            "cv_f1_mean": float(metrics["cv_f1_mean"]),
            "cv_f1_std": float(metrics["cv_f1_std"]),
            "cv_precision_mean": float(metrics["cv_precision_mean"]),
            "cv_recall_mean": float(metrics["cv_recall_mean"]),
            "cv_folds": int(metrics["cv_folds"]),
            "train_samples": int(metrics["train_samples"]),
            "test_samples": int(metrics["test_samples"]),
        },
    }


def build_markdown_report(payload: dict[str, object]) -> str:
    """Renderiza reporte Markdown legible para informe académico."""

    metrics = payload["metrics"]
    gate = payload["academic_gate"]
    dataset = payload["dataset"]
    model = payload["model"]
    gate_status = "✅ PASS" if gate["passed"] else "❌ FAIL"

    return "\n".join(
        [
            "# Evidencia automática de métricas ML",
            "",
            f"- Fecha UTC: `{payload['generated_at_utc']}`",
            f"- Estado gate académico: **{gate_status}**",
            "",
            "## Dataset evaluado",
            "",
            f"- Ruta: `{dataset['path']}`",
            f"- Tamaño default: `{dataset['default_size']}`",
            f"- Semilla default: `{dataset['default_seed']}`",
            f"- Muestras evaluadas: `{dataset['evaluated_samples']}`",
            "",
            "## Modelo",
            "",
            f"- Tipo: `{model['type']}`",
            f"- Parámetros: `{model['params']}`",
            "",
            "## Gate académico",
            "",
            f"- Accuracy mínimo: `{gate['min_accuracy']}`",
            f"- F1 mínimo: `{gate['min_f1']}`",
            "",
            "## Métricas",
            "",
            "| Métrica | Valor |",
            "|---|---:|",
            f"| accuracy | {metrics['accuracy']:.4f} |",
            f"| precision | {metrics['precision']:.4f} |",
            f"| recall | {metrics['recall']:.4f} |",
            f"| f1 | {metrics['f1']:.4f} |",
            f"| cv_f1_mean | {metrics['cv_f1_mean']:.4f} |",
            f"| cv_f1_std | {metrics['cv_f1_std']:.4f} |",
            f"| cv_precision_mean | {metrics['cv_precision_mean']:.4f} |",
            f"| cv_recall_mean | {metrics['cv_recall_mean']:.4f} |",
            f"| cv_folds | {metrics['cv_folds']} |",
            f"| train_samples | {metrics['train_samples']} |",
            f"| test_samples | {metrics['test_samples']} |",
            "",
            "## Reproducción",
            "",
            "```bash",
            "make ml-report",
            "```",
        ]
    )


def main() -> int:
    """Ejecuta evaluación y escribe artefactos JSON/Markdown."""

    args = parse_args()
    output_dir = (
        Path(args.output_dir) if args.output_dir else resolve_default_output_dir()
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = evaluate_model(dataset_path=DATA_PATH)
    payload = build_report_payload(metrics)
    markdown = build_markdown_report(payload)

    json_path = output_dir / f"{args.output_prefix}.json"
    md_path = output_dir / f"{args.output_prefix}.md"
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    md_path.write_text(f"{markdown}\n", encoding="utf-8")

    print(f"Reporte JSON generado en: {json_path}")
    print(f"Reporte Markdown generado en: {md_path}")
    print(f"Gate académico aprobado: {payload['academic_gate']['passed']}")
    print(
        "Métricas clave: "
        f"accuracy={payload['metrics']['accuracy']:.4f}, "
        f"f1={payload['metrics']['f1']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
