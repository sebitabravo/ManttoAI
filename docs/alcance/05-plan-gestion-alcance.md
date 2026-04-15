# 05. Plan de Gestión del Alcance

## Definición del Alcance
El alcance se define a partir de los requerimientos funcionales documentados en las historias de usuario de GitHub y los lineamientos de la rúbrica de INACAP.

## Control y Validación
- **Validación Interna:** A través de Pull Requests (PRs). Ningún código entra a `main` sin pasar por la validación de GitHub Actions (Lint + Tests).
- **Validación Final:** Ejecución del script `smoke_test.sh` y verificación de flujos E2E de Playwright antes de cada release.

## Roles en el Alcance
- **Sebastián B.:** Aprueba cambios que afecten arquitectura backend y DevOps.
- **Luis L.:** Documenta requerimientos en el enunciado y valida impacto en UI.
- **Ángel R.:** Define y acota el alcance del modelo predictivo (limitado a Random Forest).
