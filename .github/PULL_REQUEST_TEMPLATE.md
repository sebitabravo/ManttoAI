## 📌 Resumen ejecutivo

<!-- Máximo 3 bullets: qué cambia, por qué cambia, impacto esperado -->

-
-
-

## 🎯 Objetivo y contexto

### Problema

<!-- Qué problema real resuelve este PR -->

### Objetivo

<!-- Resultado esperado al hacer merge -->

### Alcance

- **En scope:**
- **Fuera de scope:**

## 🔗 Trazabilidad

- **Issue:** Closes #
- **Docs/ADRs relacionados (si aplica):**

### Mapa de criterios de aceptación

| Criterio de la issue | Estado (✅/⚠️/❌) | Evidencia (archivo:línea, test, comando) |
|---|---|---|
| [Completar] | [ ] | [Completar] |

## 🧩 Tipo de cambio

- [ ] 🐛 Fix (corrige bug sin breaking change)
- [ ] ✨ Feature (agrega funcionalidad sin breaking change)
- [ ] 💥 Breaking change
- [ ] 📝 Documentación
- [ ] 🎨 Refactor
- [ ] 🚀 Performance
- [ ] ⚙️ Config/Infra (Docker, CI/CD, variables, despliegue)

## 🗂️ Módulo(s) y archivos impactados

- [ ] Backend (FastAPI)
- [ ] Frontend (React)
- [ ] IoT (ESP32 / MQTT)
- [ ] ML (modelo predictivo)
- [ ] Infra (Docker, Nginx, CI/CD)

| Módulo | Archivos principales | Motivo del cambio |
|---|---|---|
| [Completar] | [Completar] | [Completar] |

## 💡 Solución técnica

### Decisiones clave

<!-- Explicar diseño elegido y por qué -->

### Alternativas consideradas (trade-offs)

| Opción | Ventaja | Costo/Riesgo | Decisión |
|---|---|---|---|
| [Completar] | [Completar] | [Completar] | [Elegida/Descartada] |

## ✅ Checklist de calidad

### Autor

- [ ] Leí `AGENTS.md` y respeté el alcance de la issue
- [ ] Hice auto-review del código
- [ ] No subí secretos ni artefactos locales (`.env`, `.db`, `modelo.joblib`, credenciales)
- [ ] El cambio es chico, reversible y alineado al MVP académico
- [ ] Actualicé documentación si correspondía

### Validación técnica ejecutada

- [ ] Backend validado (`make lint` / `make test`) si aplica
- [ ] Frontend validado (`make lint-front` / `make build-front`) si aplica
- [ ] Docker/compose validado (`docker compose config --quiet`) si aplica
- [ ] MQTT/simulador validado (`make simulate` / `make mqtt-test`) si aplica

### Evidencia de comandos

```bash
# Pegá acá comandos y resultados reales (resumidos)
# ejemplo:
# make lint -> OK
# make test -> 34 passed
```

## 🧪 Instrucciones para probar (reviewers)

### Precondiciones

<!-- Datos, variables, servicios o fixtures necesarios -->

### Pasos

1.
2.
3.

### Resultado esperado

<!-- Qué debería observar el reviewer si está correcto -->

## 📊 Impacto y riesgos

### Impacto

- [ ] 🟢 Bajo (cambio aislado)
- [ ] 🟡 Medio (afecta múltiples componentes)
- [ ] 🔴 Alto (afecta flujo crítico)

### Riesgos identificados y mitigación

| Riesgo | Severidad | Mitigación | Plan de rollback |
|---|---|---|---|
| [Completar] | [Low/Medium/High/Critical] | [Completar] | [Completar] |

### Seguridad y datos

- [ ] No se exponen secretos/credenciales
- [ ] Cambios de auth/permisos validados (si aplica)
- [ ] Migraciones y datos validados (si aplica)

## 🚀 Consideraciones de despliegue

- [ ] No requiere pasos especiales
- [ ] Requiere migración de base de datos
- [ ] Requiere actualización de configuración/variables
- [ ] Requiere coordinación/ventana de despliegue

### Plan de rollback

<!-- Paso a paso para volver atrás si falla -->

## 📸 Evidencia visual (si aplica)

<details>
<summary>Ver capturas / video</summary>

<!-- Adjuntar screenshots o video -->

</details>

## 👀 Foco para reviewers

- **Revisar primero:**
- **Áreas sensibles:**
- **Supuestos importantes:**
- **Dudas abiertas:**

## 🤖 Review asistida por IA (opcional, recomendado)

- Prompt estándar: `docs/plantilla-code-review-ia.md`
- Comentario estándar: `.github/AI_REVIEW_COMMENT_TEMPLATE.md`
