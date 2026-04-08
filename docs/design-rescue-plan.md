# Plan de Rescate UI/UX — ManttoAI Predictivo

**Fecha:** 2026-04-07  
**Rama:** `feature/ui-ux-rescue`  
**Objetivo:** llevar la UI desde patrón genérico a herramienta industrial profesional para demo de defensa.

---

## 1) Diagnóstico consolidado (audit + critique)

### Severidades priorizadas

- **P0 (bloqueantes para calidad de demo):**
  1. `frontend/src/components/ui/Modal.jsx` — declara focus trap pero no atrapa Tab (accesibilidad real incompleta).
  2. `frontend/src/components/layout/Header.jsx` — `Link` envolviendo `Button` (interactivos anidados, semántica inválida).
  3. `frontend/src/components/dashboard/TablaEstadoEquipos.jsx` — `aria-live` por fila/celda en estado de telemetría (ruido excesivo para lector de pantalla con polling).

- **P1 (impacto alto de percepción profesional):**
  1. Colores y estilo semántico por `style={{...}}` en vez de tokens/clases (`EquipoCard`, `EquipoPrediccionCard`, gráficos base).
  2. Jerarquía visual del dashboard todavía muy “grid de cards” homogéneo (necesita priorización operativa más marcada).
  3. Inconsistencia de formularios: inputs raw en umbrales vs `Input` del sistema.

- **P2 (deuda visual/consistencia):**
  1. Contraste débil en 404 (`text-neutral-300` sobre fondo claro).
  2. `Logo.jsx` usa color hex fijo fuera del sistema.
  3. Exceso de labels uppercase repetidas en tablas (fatiga visual).

- **P3 (pulido):**
  1. Unificar microcopys de estado/errores.
  2. Afinar densidad y ritmo de spacing entre secciones secundarias.

---

## 2) Lista priorizada de cambios (P0 primero)

### Fase A — Estabilización crítica (P0)
1. Corregir semántica interactiva del header.
2. Implementar focus trap real en modal.
3. Mover anuncios live a una sola región y sacar `aria-live` por celda en tabla de equipos.

### Fase B — Base visual industrial (P1)
1. `/colorize`: consolidar tokens OKLCH en Tailwind y eliminar colores inline en componentes visuales.
2. `/typeset`: reforzar jerarquía tipográfica fija + números tabulares consistentes.
3. `/arrange`: rehacer jerarquía del dashboard (alertas/riesgo dominan, resto acompaña) y limpiar ritmo de layout.

### Fase C — Consistencia sistémica (P1/P2)
1. `/normalize`: bordes, radios, sombras, paddings, botones e inputs con patrón único.

### Fase D — Pulido de entrega (P2/P3)
1. `/polish`: hover/focus/active, empty/error states accionables, skeletons consistentes y transiciones finales.

---

## 3) Archivos a tocar por fase

### 5.1 `/colorize`
- `frontend/tailwind.config.js`
- `frontend/src/index.css`
- `frontend/src/components/ui/Logo.jsx`
- `frontend/src/utils/prediccion.js` (solo mapeo visual)
- `frontend/src/components/equipos/EquipoCard.jsx`
- `frontend/src/components/equipos/EquipoPrediccionCard.jsx`
- `frontend/src/components/dashboard/GraficoLineaBase.jsx`
- `frontend/src/components/dashboard/GraficoTemperatura.jsx`
- `frontend/src/components/dashboard/GraficoVibracion.jsx`

### 5.2 `/typeset`
- `frontend/tailwind.config.js`
- `frontend/src/index.css`
- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/components/dashboard/ResumenCards.jsx`
- `frontend/src/components/dashboard/TablaEstadoEquipos.jsx`
- `frontend/src/components/dashboard/TablaUltimasLecturas.jsx`
- `frontend/src/pages/EquiposPage.jsx`
- `frontend/src/pages/AlertasPage.jsx`
- `frontend/src/pages/HistorialPage.jsx`

### 5.3 `/arrange`
- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/components/dashboard/ResumenCards.jsx`
- `frontend/src/components/dashboard/TablaEstadoEquipos.jsx`
- `frontend/src/components/dashboard/TablaUltimasLecturas.jsx`
- `frontend/src/components/layout/Layout.jsx`

### 5.4 `/normalize`
- `frontend/src/components/ui/Button.jsx`
- `frontend/src/components/ui/Input.jsx`
- `frontend/src/components/ui/Modal.jsx`
- `frontend/src/components/ui/EmptyState.jsx`
- `frontend/src/components/alertas/AlertaItem.jsx`
- `frontend/src/components/alertas/AlertaBadge.jsx`
- `frontend/src/components/equipos/EquipoUmbralesSection.jsx`
- `frontend/src/components/equipos/EquipoMantencionesSection.jsx`
- `frontend/src/components/equipos/EquipoResumenCard.jsx`

### 5.5 `/polish`
- `frontend/src/components/ui/Skeleton.jsx`
- `frontend/src/components/ui/LoadingSpinner.jsx`
- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/pages/NotFoundPage.jsx`
- `frontend/src/pages/AlertasPage.jsx`
- `frontend/src/pages/EquiposPage.jsx`

---

## 4) Qué NO se toca (explícito)

- `frontend/src/api/**`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/hooks/**`
- `frontend/src/App.jsx` (rutas)
- Lógica de negocio, contratos API, y funciones que llaman backend
- Lógica interna de procesamiento de datos de gráficos (solo estilos/colores)

---

## 5) Estimación por fase

- **Fase A (P0):** 45–70 min
- **5.1 `/colorize`:** 50–75 min
- **5.2 `/typeset`:** 35–55 min
- **5.3 `/arrange`:** 60–90 min
- **5.4 `/normalize`:** 60–90 min
- **5.5 `/polish`:** 45–70 min

**Total estimado:** 4.5–7.5 horas efectivas + revisión visual en browser.

---

## 6) Criterio de éxito

1. La pantalla de Dashboard comunica estado operativo en <3 segundos.
2. Se elimina percepción de “AI slop” (sin glow/neón/gradientes decorativos/card soup).
3. Consistencia visual transversal: radios, sombras, spacing, botones, estados.
4. Accesibilidad base sólida (focus trap, foco visible, semántica interactiva correcta).
