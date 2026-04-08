# Evidencia automática de métricas ML

- Fecha UTC: `2026-04-08T01:18:36.490346+00:00`
- Estado gate académico: **✅ PASS**

## Dataset evaluado

- Ruta: `/app/app/ml/data/synthetic_readings.csv`
- Tamaño default: `12000`
- Semilla default: `42`
- Muestras evaluadas: `12000`

## Modelo

- Tipo: `RandomForestClassifier`
- Parámetros: `{'n_estimators': 120, 'max_depth': 10, 'min_samples_leaf': 2, 'random_state': 42}`

## Gate académico

- Accuracy mínimo: `0.8`
- F1 mínimo: `0.8`

## Métricas

| Métrica | Valor |
|---|---:|
| accuracy | 0.9413 |
| precision | 0.9364 |
| recall | 0.9244 |
| f1 | 0.9304 |
| cv_f1_mean | 0.9252 |
| cv_f1_std | 0.0072 |
| cv_precision_mean | 0.9254 |
| cv_recall_mean | 0.9250 |
| cv_folds | 5 |
| train_samples | 9600 |
| test_samples | 2400 |

## Reproducción

```bash
make ml-report
```
