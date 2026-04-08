# ML ManttoAI

Este módulo contiene un pipeline reproducible para generar datos sintéticos, entrenar Random Forest y evaluar métricas de forma honesta (train/test split).

## Dataset y features

- Dataset base: `app/ml/data/synthetic_readings.csv`
- Target: `riesgo`
- Features explícitas del MVP:
  - `temperatura`
  - `humedad`
  - `vib_x`
  - `vib_y`
  - `vib_z`

La generación usa una semilla fija por defecto para que el pipeline sea repetible en la memoria técnica.

Tamaño por defecto del dataset sintético: **12.000 filas**.

## Modelo

- Algoritmo: `RandomForestClassifier`
- Artefacto: `app/ml/modelo.joblib`
- El artefacto queda fuera de git por `.gitignore`.
- El build Docker omite entrenamiento por defecto (`SKIP_TRAIN=true`).
- Si se necesita incluir artefacto en imagen: build con `--build-arg SKIP_TRAIN=false`.

## Comandos

```bash
cd backend/app/ml
../../.venv/bin/python generate_dataset.py
../../.venv/bin/python train.py
../../.venv/bin/python evaluate.py
```

## Métricas esperadas (referencia MVP)

En dataset sintético reproducible, la evaluación debería reportar métricas estables entre ejecuciones cercanas, normalmente con `accuracy` y `f1` sobre 0.80 para cumplir el objetivo académico del prototipo.

## Seguridad del artefacto

`joblib` usa serialización basada en pickle. Por eso:

- no cargues `modelo.joblib` desde fuentes no confiables
- regenerá el modelo localmente con `train.py` cuando haya dudas
