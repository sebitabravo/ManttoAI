# Datasets ML

Este directorio guarda datasets de prueba o referencia.

- `synthetic_readings.csv`: dataset sintético generado localmente
- referencias externas como NASA C-MAPSS deben documentarse antes de agregarse

Para regenerar el dataset sintético reproducible:

```bash
cd backend/app/ml
../../.venv/bin/python generate_dataset.py
```
