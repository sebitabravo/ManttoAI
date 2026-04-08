# Evidencia ML (última corrida)

**Fuente:** `backend/reports/ml-evaluation-latest.json`  
**Comando de reproducción:** `make ml-report`

## Resultado

- Fecha UTC: `2026-04-08T01:16:54.000960+00:00`
- Dataset evaluado: `12000` muestras
- Gate académico (`accuracy>=0.80` y `f1>=0.80`): **✅ PASS**

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

## Parámetros del modelo

- Tipo: `RandomForestClassifier`
- `n_estimators=120`
- `max_depth=10`
- `min_samples_leaf=2`
- `random_state=42`
