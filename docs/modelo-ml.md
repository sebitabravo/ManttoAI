# Modelo ML

El proyecto usa un pipeline reproducible basado en Random Forest para soportar la predicción de riesgo del MVP.

## Dataset y target

- Dataset sintético: `backend/app/ml/data/synthetic_readings.csv`
- Target: `riesgo`
- Features explícitas:
  - `temperatura`
  - `humedad`
  - `vib_x`
  - `vib_y`
  - `vib_z`

La generación es reproducible con semilla fija para facilitar repetición en informe y demo.

Tamaño por defecto del dataset sintético: **12.000 registros**.

Si existe un dataset previo con menos registros, el pipeline lo regenera automáticamente
para cumplir el mínimo configurado.

## Entrenamiento

- Script: `backend/app/ml/train.py`
- Modelo: `RandomForestClassifier`
- Artefacto: `backend/app/ml/modelo.joblib` (ignorado por git)
- Checksum sidecar: `backend/app/ml/modelo.joblib.sha256`

> En Docker, el build del backend **omite** entrenamiento por defecto (`SKIP_TRAIN=true`) para mantener builds rápidos.
> Si necesitás artefacto embebido en imagen, build con `--build-arg SKIP_TRAIN=false`.
> En runtime, si el artefacto falta y `ML_AUTO_TRAIN_ON_MISSING=true`, se reentrena automáticamente.

Comando:

```bash
cd backend/app/ml
../../.venv/bin/python train.py
```

## Evaluación honesta

- Script: `backend/app/ml/evaluate.py`
- Estrategia: separación train/test con `stratify` para evitar leakage
- Métricas reportadas:
  - accuracy
  - precision
  - recall
  - f1
  - train_samples
  - test_samples
- Gate académico mínimo: `f1 >= 0.80` en tests automatizados

Comando:

```bash
cd backend/app/ml
../../.venv/bin/python evaluate.py
```

## Evidencia automática de métricas (recomendado para defensa)

Se puede generar un reporte reproducible (JSON + Markdown) con:

```bash
make ml-report
```

Artefactos generados:

- `backend/reports/ml-evaluation-latest.json`
- `backend/reports/ml-evaluation-latest.md`

El reporte incluye:

- timestamp UTC de ejecución,
- tamaño real de muestras evaluadas,
- accuracy/F1 y métricas CV,
- validación explícita del gate académico (`accuracy >= 0.80` y `f1 >= 0.80`).

## Generación de dataset

```bash
cd backend/app/ml
../../.venv/bin/python generate_dataset.py
```

## Notas de alcance

- No se usa deep learning.
- No se hace tuning exhaustivo.
- El objetivo es trazabilidad y reproducibilidad para el informe académico.

## Seguridad de carga de modelos

El artefacto `.joblib` debe tratarse como archivo confiable local.

- No cargar modelos descargados de orígenes no verificados.
- El loader verifica integridad con checksum SHA-256 sidecar antes de cargar el artefacto.
- Ante dudas, regenerar dataset y modelo con `generate_dataset.py` y `train.py`.

## Runbook operativo breve

1. Regenerar dataset si hace falta: `python generate_dataset.py`
2. Reentrenar modelo: `python train.py`
3. Evaluar métricas: `python evaluate.py`
4. Verificar que el test automatizado de `f1 >= 0.80` siga pasando
5. Si una versión nueva falla, regenerar el artefacto previo conocido y su checksum sidecar
