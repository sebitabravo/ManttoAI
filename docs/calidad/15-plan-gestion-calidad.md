# 15. Plan de Gestión de Calidad

**Estándares Aplicables:** Basado en ISO/IEC 25010.
- **Functional Suitability:** Modelo de IA (F1-Score).
- **Maintainability:** Código limpio (Ruff, Black, ESLint) y cobertura de tests (Pytest > 70%).
- **Reliability:** Despliegue Dockerizado inmutable.

**Actividades de Aseguramiento (QA):**
- Ejecución automática de GitHub Actions en cada Push/PR.
- Code Review asistido por IA (`code-reviewer`).

**Actividades de Control:**
- Verificación del F1-Score mediante Scikit-learn (Cross-validation).
- Ejecución de `playwright test` para evitar regresiones visuales.
