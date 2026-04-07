# Bugs detectados durante QA final — Issue #50

Documento de consolidación de todos los bugs encontrados en las etapas de
QA manual, E2E, smoke test y validación de hardware.

> Issue paraguas: #50 — fix: corregir bugs detectados durante QA final

---

## Estado de bugs por severidad

### 🔴 Críticos (bloqueantes para demo/defensa)

| # | Bug | Detectado en | Corregido en | PR | Estado |
|---|---|---|---|---|---|
| B-01 | Clasificaciones del modelo desalineadas: `prediccion.js` usaba `"advertencia"`/`"critico"` pero el backend devuelve `"alerta"`/`"falla"` → todos los badges mostraban `"Sin predicción"` | Issue #49 QA manual | Issue #49 | PR #77 | ✅ Cerrado |
| B-02 | `dashboard_service.py` no incluía `clasificacion` en la subquery SQL → `ultima_clasificacion` llegaba siempre `null` al frontend | Issue #49 QA manual | Issue #49 | PR #77 | ✅ Cerrado |
| B-03 | Puerto 5173 duplicado en `docker-compose.yml` + override → stack no levantaba (`Bind for 0.0.0.0:5173 failed`) | Issue #44 smoke test | Issue #44 | PR #76 | ✅ Cerrado |
| B-04 | `smoke_test.sh` hacía `login_backend` antes de `make seed` → 401 en DB limpia | Issue #44 smoke test | Issue #44 | PR #76 | ✅ Cerrado |
| B-05 | `source backend/.env` con `set -euo pipefail` → `APP_NAME` con espacios mataba el script | Issue #44 smoke test | Issue #44 | PR #76 | ✅ Cerrado |

### 🟡 Altos (afectan funcionalidad pero no bloquean demo)

| # | Bug | Detectado en | Corregido en | PR | Estado |
|---|---|---|---|---|---|
| B-06 | `test_mqtt_simulator.py` fallaba en contenedor Docker porque `iot/simulator/` no estaba montado en `/iot` | Issue #50 audit | Issue #50 | PR #78 | ✅ Cerrado |
| B-07 | `DashboardEquipoResumen` schema no tenía `ultima_clasificacion` → campo no se serializaba en la respuesta de la API | Issue #49 QA manual | Issue #49 | PR #77 | ✅ Cerrado |

### 🟢 Bajos / Cosméticos (no bloquean demo)

| # | Bug | Detectado en | Estado |
|---|---|---|---|
| B-08 | Tipos de alerta en `/alertas` muestran `"prediccion"`, `"temperatura"`, `"vibracion"` en minúsculas sin capitalizar | Issue #49 QA manual | Documentado — no bloquea demo |

---

## Bugs bloqueantes abiertos al cierre de esta issue

**Ninguno.** Todos los bugs críticos y altos detectados durante QA fueron corregidos.

---

## Cobertura de tests al cierre

| Suite | Resultado |
|---|---|
| Backend pytest (105 tests) | ✅ 105/105 (2 skipped por SMTP no configurado) |
| Frontend unit tests Vitest (26 tests) | ✅ 26/26 |
| E2E Playwright Chromium (4 tests) | ✅ 4/4 |
| E2E Playwright Firefox (4 tests) | ✅ 4/4 |
| Smoke test completo | ✅ 4/4 escenarios |

---

## Criterios de aceptación — estado final

- [x] Todos los bugs críticos/altos detectados quedaron registrados
- [x] Cada bug tiene PR asociado y estado claro
- [x] No quedan bugs bloqueantes abiertos al cerrar la issue
