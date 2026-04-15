# 16. Métricas de Calidad

De acuerdo al estándar ISO/IEC 25010 y a los requerimientos del proyecto, se establecieron las siguientes métricas evaluables objetivamente contra el código fuente:

| Métrica | Dimensión ISO | Valor Objetivo | Método de Medición |
|---------|---------------|----------------|--------------------|
| F1-Score Modelo ML | Funcionalidad | ≥ 80% | Reporte Scikit-Learn |
| Cobertura Tests API | Mantenibilidad | ≥ 70% | `pytest --cov=app` |
| Lint Warnings (Backend) | Mantenibilidad | 0 | `ruff check .` |
| Pruebas E2E (Frontend) | Fiabilidad | ≥ 5 flujos | Playwright test suite |
| Tiempos de Respuesta API | Rendimiento | < 500ms | Mediciones de Red / Axios |
| Uptime de Servicios | Fiabilidad | > 99% | Logs de Docker Compose |
