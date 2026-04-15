# 08. Matriz de Trazabilidad de Requisitos

| ID | Descripción | Entregable | Estado | Evidencia en Repo |
|----|-------------|------------|--------|-------------------|
| RF01 | Recepción MQTT de sensores | E2 Pipeline | ✅ | `backend/app/services/mqtt_service.py` |
| RF02 | Persistencia de lecturas | E2 Pipeline | ✅ | `backend/app/models/lectura.py` |
| RF03 | Evaluación de umbrales | E2 Pipeline | ✅ | `backend/app/services/alertas_service.py` |
| RF04 | Predicción de fallas ML | E3 Modelo IA | ✅ | `backend/app/ml/predict.py` |
| RF05 | Visualización de equipos | E4 Dashboard | ✅ | `frontend/src/pages/Equipos.jsx` |
| RF06 | Auto-refresh de datos | E4 Dashboard | ✅ | `frontend/src/hooks/usePolling.js` (Lógica implementada) |
| RNF01| Cobertura de tests > 70% | E6 QA | ✅ | `pytest --cov` (82% real) |
| RNF02| Contenedores Docker | E5 Infra | ✅ | `docker-compose.yml` |
| RNF03| CI/CD Automatizado | E5 Infra | ✅ | `.github/workflows/` |
