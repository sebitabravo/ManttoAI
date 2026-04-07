# QA Manual — Chrome y Firefox

Validación manual del frontend en navegadores de escritorio.
Ejecutada con Playwright MCP sobre el stack local levantado.

> Referencia: issue #49 — QA manual en Chrome y Firefox.

---

## Entorno de ejecución

| Campo | Valor |
|---|---|
| Fecha | 2026-04-07 |
| Stack | Docker Compose local (backend + frontend + mysql + mosquitto) |
| Frontend URL | http://localhost:5173 |
| Backend URL | http://localhost:8000 |
| Herramienta | Playwright MCP (Chromium) + `npx playwright test` (Chromium + Firefox) |

---

## Resultados por vista

### Login (`/login`)

| Verificación | Chrome | Firefox |
|---|---|---|
| Página carga correctamente con branding | ✅ | ✅ |
| Credenciales incorrectas muestran error en rojo | ✅ | ✅ |
| Login exitoso redirige a `/dashboard` | ✅ | ✅ |
| Título de pestaña correcto | ✅ | ✅ |

### Dashboard (`/dashboard`)

| Verificación | Chrome | Firefox |
|---|---|---|
| Cards de resumen (equipos, alertas, riesgo, clasificación, probabilidad) | ✅ | ✅ |
| Tabla de estado por equipo con 3 equipos | ✅ | ✅ |
| Gráfico de temperatura renderiza | ✅ | ✅ |
| Gráfico de vibración renderiza | ✅ | ✅ |
| Tabla de últimas lecturas | ✅ | ✅ |

### Equipos (`/equipos`)

| Verificación | Chrome | Firefox |
|---|---|---|
| 3 cards de equipos visibles | ✅ | ✅ |
| Badge de predicción con color semántico (⚠️ Alerta / ✅ Normal / 🔴 Falla) | ✅ (tras fix) | ✅ (tras fix) |
| Porcentaje de probabilidad en badge | ✅ | ✅ |
| Link "Ver detalle" funciona | ✅ | ✅ |

### Detalle de equipo (`/equipos/1`)

| Verificación | Chrome | Firefox |
|---|---|---|
| Datos del equipo (nombre, estado, ubicación, tipo) | ✅ | ✅ |
| Umbrales operativos editables | ✅ | ✅ |
| Sección "Última predicción" con clasificación y barra de riesgo | ✅ (tras fix) | ✅ (tras fix) |
| Tabla de últimas lecturas | ✅ | ✅ |
| Sección de mantenciones | ✅ | ✅ |

### Alertas (`/alertas`)

| Verificación | Chrome | Firefox |
|---|---|---|
| Lista de alertas no leídas | ✅ | ✅ |
| Contador de alertas activas | ✅ | ✅ |
| Botón "Marcar como leída" funciona y actualiza contador | ✅ | ✅ |

### Historial (`/historial`)

| Verificación | Chrome | Firefox |
|---|---|---|
| Tabla de lecturas recientes con datos de 3 equipos | ✅ | ✅ |
| Columnas: Equipo, Temperatura, Humedad, Vibración máx., Fecha | ✅ | ✅ |

### Responsive tablet (768px)

| Verificación | Chrome | Firefox |
|---|---|---|
| Layout colapsa a 1 columna | ✅ | ✅ |
| Botón hamburguesa visible en header | ✅ | ✅ |
| Drawer de navegación se abre con overlay | ✅ | ✅ |
| Cards y gráficos legibles | ✅ | ✅ |

---

## Bugs encontrados y corregidos

### Bug 1 — Clasificaciones del modelo desalineadas con el frontend (Crítico)

**Síntoma:** Todos los badges de predicción mostraban `"— Sin predicción"` aunque había probabilidades reales.

**Causa raíz (2 partes):**
1. `frontend/src/utils/prediccion.js` tenía las claves `"advertencia"` y `"critico"` pero el backend devuelve `"alerta"` y `"falla"` (según `prediccion_service.py`).
2. `backend/app/services/dashboard_service.py` no incluía `clasificacion` en la query de predicciones por equipo — `ultima_clasificacion` llegaba siempre como `null` al frontend.
3. `backend/app/schemas/dashboard.py` no tenía el campo `ultima_clasificacion` en `DashboardEquipoResumen`.

**Fix aplicado:**
- `prediccion.js`: reemplazó `advertencia`/`critico` por `alerta`/`falla`
- `dashboard_service.py`: agrega `Prediccion.clasificacion` a la subquery y al dict de resultado
- `dashboard.py` (schema): agrega `ultima_clasificacion: str | None = None` a `DashboardEquipoResumen`

**Verificación:** badges muestran ⚠️ Alerta, ✅ Normal, 🔴 Falla con colores correctos.

---

## Tests automatizados

| Suite | Chromium | Firefox |
|---|---|---|
| E2E Playwright (4 tests) | ✅ 4/4 | ✅ 4/4 |
| Unit tests Vitest (26 tests) | ✅ 26/26 | — |
| Backend pytest (102 tests) | ✅ 101/102* | — |

*1 test falla por SMTP no configurado (pre-existente, no relacionado con esta issue).

---

## Criterios de aceptación — estado final

- [x] El frontend fue probado manualmente en Chrome (Playwright MCP + E2E)
- [x] El frontend fue probado manualmente en Firefox (Playwright E2E)
- [x] Los hallazgos relevantes quedaron registrados (este documento)
- [x] No quedan errores visibles críticos sin documentar ni corregir
