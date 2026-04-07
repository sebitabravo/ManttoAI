# Plan de Rescate UI/UX — ManttoAI Predictivo

**Autor:** Sebastian Bravo
**Fecha:** 7 de abril, 2026
**Objetivo:** Transformar el frontend de "AI slop" genérico a herramienta profesional industrial antes de la defensa de título
**Rama de trabajo:** `feature/ui-ux-rescue`

---

## Contexto

El frontend actual fue generado por IA en iteraciones anteriores y presenta múltiples anti-patterns de "AI slop":

- Cards con `rounded-2xl` genérico
- Colores Tailwind defaults sin customización (gray-200, gray-500, blue-700)
- Sin jerarquía visual: todo compite por atención
- Tailwind config vacío, tokens no integrados
- Responsive issues en tablas
- Touch targets < 44px
- Accesibilidad parcial (focus-visible faltante, Modal sin focus trap)

**Audit Health Score:** 6/20 (POOR)
**Design Health Score (Nielsen):** 21/40 (ACCEPTABLE)
**AI Slop Test:** ❌ FAIL — se nota que fue generado por IA

---

## Principios de Diseño (de `.impeccable.md`)

1. **Data is the Hero** — Los números, estados, y tendencias son lo más importante
2. **Scannable, Not Scrollable** — El usuario debe evaluar el estado en < 3 segundos
3. **Industrial, Not Decorative** — Cada elemento debe tener función
4. **Consistency Over Creativity** — Replica el mismo estilo en toda la app
5. **Clarity Under Pressure** — En alta carga cognitiva, simplificar no complicar

---

## Issues Encontrados

### Distribución por Severidad

| Severidad | Cantidad | Categoría Principal |
|-----------|----------|---------------------|
| P0 Bloqueantes | 12 | Theming, Responsive, A11y |
| P1 Mayores | 23 | Colores hard-coded, Touch targets, Border radius |
| P2 Menores | 31 | Inline styles, Font sizes, Dark mode prep |
| P3 Polish | 23 | Emojis, Timings, Sticky headers |
| **TOTAL** | **89** | |

### Top 10 Críticos (P0/P1)

1. **[P0-THEME] Tailwind config vacío** — `tokens.js` no integrado, colores hard-coded en 20+ archivos
2. **[P0-RESP] Tablas no responsive** — Rompen < 640px, overflow horizontal
3. **[P0-A11Y] Modal sin focus trap** — Usuarios de teclado atrapados
4. **[P0-A11Y] Inputs sin labels visibles** — Solo `aria-label`, viola WCAG
5. **[P0-PERF] Polling sin backoff** — Requests sin pause cuando tab hidden
6. **[P1-THEME] Colores hard-coded** — 20+ componentes con hex codes inline
7. **[P1-THEME] Border radius inconsistente** — Mezcla 8px, 10px, 12px, 16px, 18px, 9999px
8. **[P1-RESP] Touch targets < 44px** — Botones e inputs difíciles de tocar en móvil
9. **[P1-ANTI] rounded-2xl AI slop** — En 8+ componentes, estética genérica
10. **[P1-DESIGN] ResumenCards sin jerarquía** — 5 cards iguales, alertas no destacan

---

## Estrategia de Ejecución

### Orden de Comandos (PASO 5)

Vamos a ejecutar los comandos de skills en este orden estricto:

#### **5.1) `/colorize` — Paleta de colores industrial**

**Objetivo:**

- Definir paleta OKLCH profesional para contexto industrial
- Neutrales tintados azul-grisáceo (NO gris puro)
- Primario: azul petróleo sobrio (#0066cc aprox, no #1d4ed8 genérico)
- Estados semánticos SATURADOS: verde/amarillo/rojo profesionales
- NUNCA pure black (#000) ni pure white (#fff)

**Archivos a modificar:**

- `frontend/tailwind.config.js` — Extender `theme.extend.colors`
- `frontend/src/styles/tokens.js` — Reemplazar colores por OKLCH
- `frontend/src/components/ui/Logo.jsx` — Actualizar `BRAND_COLOR`
- `frontend/src/index.css` — Definir CSS variables para theming

**Output esperado:**

- Palette definida en tokens: `PRIMARY`, `NEUTRAL_50-900`, `SUCCESS`, `WARNING`, `DANGER`, `INFO`
- Todos los colores en OKLCH para mejor perceptual uniformity
- Tailwind config exporta colores custom: `bg-primary`, `text-neutral-700`, etc.

**NO tocar:**

- Lógica de negocio
- Llamadas API
- Hooks

---

#### **5.2) `/typeset` — Jerarquía tipográfica**

**Objetivo:**

- NO usar Inter (fuente AI slop por defecto)
- Considerar: Geist, IBM Plex Sans, Söhne, o JetBrains Mono para valores numéricos
- Escala fija: máximo 4 tamaños distintos en uso
- Tabular nums (`font-variant-numeric: tabular-nums`) para valores de sensores
- Peso variable: Regular (400), Medium (500), Semibold (600)

**Archivos a modificar:**

- `frontend/tailwind.config.js` — Extender `theme.extend.fontFamily` y `fontSize`
- `frontend/src/index.css` — Importar fonts si es custom (font-display: swap)
- `frontend/src/styles/tokens.js` — Actualizar `FONT_SIZE` tokens
- Componentes con valores numéricos: agregar `tabular-nums`

**Output esperado:**

- Font stack definido: `--font-sans: "Geist", system-ui, sans-serif` (o similar)
- Escala: `xs: 12px, sm: 13px, base: 14px, md: 16px, lg: 20px, xl: 24px`
- Clase `.tabular-nums` aplicada en tablas y cards de resumen
- Jerarquía clara: h1 > h2 > body > caption

**NO tocar:**

- Estructura JSX (solo clases de estilo)
- Lógica de componentes

---

#### **5.3) `/arrange` — Layout y spacing con ritmo visual**

**Objetivo:**

- Eliminar cards anidadas dentro de cards
- Crear ritmo visual con spacing variado (NO todo `gap-4`)
- Dashboard con jerarquía: alertas críticas ocupan más espacio
- Grid system real, no flex aleatorio
- ResumenCards con layout asimétrico: Alertas GRANDE, Equipos en riesgo PROMINENTE, resto secundario

**Archivos a modificar:**

- `frontend/src/components/dashboard/ResumenCards.jsx` — Rediseñar layout
- `frontend/src/pages/DashboardPage.jsx` — Ajustar spacing entre secciones
- `frontend/src/components/dashboard/TablaEstadoEquipos.jsx` — Jerarquía visual en columnas
- `frontend/tailwind.config.js` — Definir spacing custom si necesario

**Output esperado:**

- ResumenCards tipo Datadog: Alertas activas 2x size si > 0, fondo rojo
- Equipos en riesgo 1.5x size, fondo amarillo si > 0
- Total equipos, Clasificación, Probabilidad: cards secundarios pequeños
- Spacing variado: `gap-6` entre secciones principales, `gap-4` interno en cards
- TablaEstadoEquipos: columna "Alertas activas" con fondo rojo si > 0, bold

**NO tocar:**

- Props de componentes
- Lógica de formateo (metrics.js, formatDate.js)
- Llamadas API

---

#### **5.4) `/normalize` — Consistencia en TODOS los componentes**

**Objetivo:**

- Integrar `tokens.js` con `tailwind.config.js` (extender theme)
- Mismos border-radius en todo: eliminar `rounded-2xl`, estandarizar
- Mismas sombras: definir 2-3 niveles de elevación (`shadow-sm`, `shadow-md`, custom)
- Mismos paddings en cards similares
- Mismo estilo de botones en toda la app
- Migrar inline styles a Tailwind classes donde posible

**Archivos a modificar:**

- `frontend/tailwind.config.js` — Extender `borderRadius`, `boxShadow`, `spacing`
- `frontend/src/styles/tokens.js` — Exportar tokens a formato Tailwind-compatible
- `frontend/src/components/ui/Button.jsx` — Migrar inline styles a clases
- `frontend/src/components/ui/Input.jsx` — Unificar estilos
- TODOS los componentes con `rounded-2xl` → reemplazar por token standard
- TODOS los componentes con inline `style={{}}` → migrar a Tailwind

**Output esperado:**

- `tailwind.config.js` con:
  - `theme.extend.colors` desde tokens
  - `theme.extend.spacing` desde tokens
  - `theme.extend.borderRadius: { sm: '8px', md: '10px', lg: '16px', full: '9999px' }`
  - `theme.extend.boxShadow: { sm: '...', md: '...' }`
- Todos los componentes usan clases consistentes: `rounded-lg`, `shadow-sm`, `p-4`
- NO hay `rounded-2xl` en ningún lado
- NO hay colores hex inline (todos via clases Tailwind custom)

**NO tocar:**

- Lógica de negocio
- Event handlers
- Props validation

---

#### **5.5) `/polish` — Pulido final**

**Objetivo:**

- Estados hover, focus, active en TODOS los elementos interactivos
- Loading states con skeleton screens (no spinners genéricos)
- Empty states con mensaje y CTA claro
- Error states que ayuden a resolver (botón "Reintentar", timestamp)
- Transiciones 150-300ms con easing `ease-out-quart`
- Tabular nums en todos los datos numéricos (si no se hizo en typeset)
- Sticky headers en tablas mobile
- Visual spinner en LoadingSpinner

**Archivos a modificar:**

- `frontend/src/components/ui/LoadingSpinner.jsx` — Agregar spinner CSS animado
- `frontend/src/components/ui/Button.jsx` — Agregar `:hover`, `:focus-visible`, `:active`
- `frontend/src/components/ui/Modal.jsx` — Focus trap, Escape key, retorno de foco
- `frontend/src/components/ui/Input.jsx` — Focus-visible con outline
- `frontend/src/pages/DashboardPage.jsx` — Error state con botón "Reintentar" y timestamp
- `frontend/src/components/ui/EmptyState.jsx` — Mejorar mensaje y CTA
- `frontend/src/index.css` — Definir transitions custom, skeleton screen animations
- TODAS las tablas — Sticky headers con `position: sticky` en `<thead>`

**Output esperado:**

- Button con `:hover` (darken 10%), `:active` (scale 0.98), `:focus-visible` (outline blue)
- LoadingSpinner con SVG spinner rotando o CSS `@keyframes spin`
- Modal con focus trap (focus en primer input al abrir, retorna a trigger al cerrar)
- Error state: "No se pudo actualizar. Última actualización: hace 2 min. [Botón Reintentar]"
- Transitions: `transition-all duration-200 ease-out`
- Tablas con `<thead className="sticky top-0 bg-white z-10">`

**NO tocar:**

- Lógica de polling (usePolling hook)
- Llamadas API
- Validaciones de formularios

---

## Archivos a NO Tocar (CRÍTICO)

❌ **NUNCA modificar:**

- `frontend/src/api/` — Cliente HTTP
- `frontend/src/context/AuthContext.jsx` — Lógica de auth
- `frontend/src/hooks/` — Custom hooks (usePolling, useAuth, etc.)
- `frontend/src/utils/` — Utilidades (metrics.js, formatDate.js, constants.js)
- `frontend/src/App.jsx` — Routing
- Funciones que llaman backend
- Lógica de Chart.js (mantener, solo cambiar colores/estilos)

✅ **SÍ modificar:**

- Todo lo visual: clases Tailwind, estructura JSX de presentación
- `frontend/tailwind.config.js`
- `frontend/src/styles/tokens.js`
- `frontend/src/components/ui/` (Button, Input, Modal, etc.)
- `frontend/src/components/layout/` (Sidebar, Header, Layout)
- `frontend/src/index.css`
- Cualquier componente de presentación en `src/components/` y `src/pages/`

---

## Estrategia de Testing

**Pre-ejecución:**

- ✅ Levantar frontend local: `npm run dev` (puerto 5173)
- ✅ Verificar que no hay errores de compilación

**Post cada comando:**

- Verificar en browser que los cambios se aplican correctamente
- Verificar que NO se rompió funcionalidad existente (clicks, navegación, polling)
- Commit granular con mensaje descriptivo: `feat(ui): apply /colorize - OKLCH palette`

**Verificación final:**

- Abrir Dashboard y verificar:
  - Alertas activas destacan visualmente
  - Colores profesionales (no AI slop)
  - Tablas legibles en mobile (overflow-x-auto)
  - Botones touch-friendly (44px min)
  - Loading spinner visible
  - Error state con retry button
  - Focus-visible en todos los interactivos
- Run `npm run build` para verificar que no hay errores de producción
- Opcional: tomar screenshots antes/después con Playwright

---

## Commits Planeados

Estructura de commits en `feature/ui-ux-rescue`:

```
1. feat(ui): apply /colorize - define OKLCH industrial palette
2. feat(ui): integrate tokens with tailwind config
3. feat(ui): apply /typeset - typography hierarchy with Geist
4. feat(ui): apply /arrange - dashboard layout with visual hierarchy
5. feat(ui): redesign ResumenCards with asymmetric critical metrics
6. feat(ui): apply /normalize - standardize border-radius and shadows
7. feat(ui): migrate inline styles to Tailwind classes
8. feat(ui): apply /polish - interaction states and loading UX
9. feat(ui): add focus-visible to all interactive elements
10. feat(ui): implement responsive tables with overflow-x-auto
11. feat(ui): add visual spinner to LoadingSpinner
12. feat(ui): improve error state with retry and timestamp
13. docs: update design-rescue-plan with completion status
```

---

## Estimación de Tiempo

| Comando | Tiempo Estimado | Archivos Modificados |
|---------|-----------------|----------------------|
| `/colorize` | 30-45 min | tailwind.config.js, tokens.js, Logo.jsx, index.css |
| `/typeset` | 20-30 min | tailwind.config.js, tokens.js, index.css, componentes con números |
| `/arrange` | 45-60 min | ResumenCards.jsx, DashboardPage.jsx, TablaEstadoEquipos.jsx |
| `/normalize` | 60-90 min | tailwind.config.js, tokens.js, 20+ componentes con rounded-2xl |
| `/polish` | 45-60 min | LoadingSpinner.jsx, Button.jsx, Modal.jsx, Input.jsx, tablas |
| **TOTAL** | **3-4.5 horas** | ~30-40 archivos |

---

## Criterios de Éxito

Al finalizar el rescue, el frontend debe cumplir:

### Funcionales

- ✅ NO se rompe ninguna funcionalidad existente (polling, navegación, auth, formularios)
- ✅ Build de producción exitoso (`npm run build`)
- ✅ No hay errores de consola

### Visuales

- ✅ Paleta de colores industrial profesional (NO AI slop)
- ✅ Jerarquía visual clara: alertas críticas destacan
- ✅ Border-radius consistente en TODA la app
- ✅ Spacing con ritmo visual (no todo gap-4)
- ✅ Tipografía con jerarquía clara (max 4 tamaños)

### Accesibilidad

- ✅ Focus-visible en TODOS los elementos interactivos
- ✅ Touch targets >= 44px
- ✅ Modal con focus trap
- ✅ Inputs con labels visibles
- ✅ Loading spinner visible para usuarios videntes

### Responsive

- ✅ Tablas responsive (overflow-x-auto o card layout < 768px)
- ✅ ResumenCards 1 columna < 480px
- ✅ Gráficos 1 columna < 900px

### Performance

- ✅ Lazy loading de rutas con React.lazy (si tiempo permite)
- ✅ Polling con Page Visibility API (si tiempo permite)
- ✅ Memoización en cálculos costosos (si tiempo permite)

### "AI Slop Test"

- ✅ **PASS** — Si alguien pregunta "¿esto lo hizo una IA?", la respuesta debe ser "no, lo hizo un equipo de diseño"

---

## Rollback Plan

Si algo se rompe durante la ejecución:

1. **Commit frecuente** permite revert granular: `git revert <commit-hash>`
2. **Rama separada** permite abandonar y volver a `develop`: `git checkout develop`
3. **Stash changes** si hay conflictos: `git stash && git checkout develop`

**Nunca hacer:**

- Force push a `main` o `develop`
- Merge sin code review (aunque sea auto-review)
- Deploy a producción sin verificar en local

---

## Post-Rescue Actions

Después de completar el rescue:

1. **Crear PR** contra `develop`:

   ```bash
   gh pr create --title "feat(ui): rescue UI/UX from AI slop to professional industrial design" \
                --body "$(cat docs/design-rescue-plan.md | head -50)"
   ```

2. **Self code-review** con `/code-review-pro`:
   - Verificar que no se tocó lógica de negocio
   - Verificar que no hay colores hard-coded residuales
   - Verificar consistencia de border-radius
   - Verificar a11y (focus-visible, labels, ARIA)

3. **Re-run audits**:
   - `/audit` para verificar score improvement (target: 14+/20)
   - `/critique` para verificar heuristics (target: 28+/40)

4. **Update documentación**:
   - `docs/manual-usuario.md` con screenshots nuevos (si aplica)
   - `docs/demo.md` con guía visual actualizada
   - `README.md` frontend con nota de diseño actualizado

5. **Merge y deploy**:
   - Merge PR a `develop`
   - Verificar en staging (Dokploy preview si existe)
   - Merge a `main` solo después de QA manual

---

## Notas Finales

- **Prioridad:** Funcionalidad > Estética. Si algo rompe, rollback inmediato.
- **Filosofía:** Industrial, no decorativo. Cada píxel debe tener función.
- **Objetivo:** Que un técnico en planta pueda evaluar el estado en < 3 segundos.
- **Vara de calidad:** "¿Esto lo hizo una IA?" → respuesta debe ser "NO".

**Última actualización:** 7 de abril, 2026 — Pre-ejecución
**Estado:** ⏳ Pendiente ejecución de comandos
**Próximo paso:** Ejecutar PASO 5.1 (`/colorize`)
