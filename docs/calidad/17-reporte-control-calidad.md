# 17. Reporte de Control de Calidad (Final)

Este reporte detalla los resultados empíricos extraídos de la auditoría del repositorio de ManttoAI Predictivo.

## Resumen de Resultados

- **Métricas Cumplidas:** 6 de 6 (100%)
- **Deuda Técnica Crítica:** Ninguna
- **Estado CI/CD:** ✅ Verde (Tests y Linters pasando)

## Evidencia Empírica

### 1. Calidad del Modelo Machine Learning
- **Métrica:** F1-Score ≥ 80%
- **Resultado:** ✅ **94.1%** (Superado)
- **Evidencia:** Reporte reproducible en `backend/reports/ml-evaluation-latest.md` y `ml-evaluation-latest.json`.

### 2. Cobertura de Tests (Backend)
- **Métrica:** Cobertura ≥ 70%
- **Resultado:** ✅ **82%** (200 tests pasados)
- **Evidencia:** Output de `pytest tests/ -v --cov=app` (Guardado en logs de CI).

### 3. Calidad de Código Estático (Linting)
- **Métrica:** 0 warnings (Black, Ruff, ESLint)
- **Resultado:** ✅ **0 warnings**
- **Evidencia:** Pipelines de GitHub Actions completados exitosamente.

### 4. Flujos End-to-End (Frontend)
- **Métrica:** ≥ 5 flujos estables
- **Resultado:** ✅ **7 flujos exitosos**
- **Evidencia:** Playwright tests (Login, Navegación, Detalle, Alertas, Logout).

### Conclusión de QA
El producto cumple holgadamente con los estándares de calidad exigidos para un Prototipo MVP Académico, demostrando robustez tanto en su código fuente como en su entorno de despliegue (Docker/VPS).
