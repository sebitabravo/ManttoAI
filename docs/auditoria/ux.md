# Auditoría UX — Recruiter-facing impression (ManttoAI dashboard)

> **Nota de estado:** este documento conserva la línea base capturada antes de
> las correcciones. El estado actual de esos hallazgos se registra en
> `docs/auditoria/estado-implementacion.md`: timeout y mensaje de cold-start,
> estado de error sin métricas ficticias, contraste secundario y touch target
> de `Input` ya fueron corregidos localmente. `LoginPage` ahora permite
> configurar un botón de acceso demo que solo rellena una cuenta read-only;
> sigue dependiendo de que exista una cuenta pública autorizada y de que el
> deployment configure explícitamente sus variables Vite.

> Revisión de código estático (`frontend/src/`). No se ejecutó el dev server ni se
> capturaron screenshots — el agente no tuvo acceso a shell en esta sesión. Los
> hallazgos de layout/responsive/contraste están verificados leyendo Tailwind
> config, CSS y JSX directamente (clases, tokens de color, breakpoints), no
> observados en navegador. Se recomienda una pasada visual manual (`npm run dev`
> + DevTools responsive mode) antes de dar por cerrada esta auditoría.

## Resumen

**Impresión recruiter-facing estimada: 6/10.** El sistema de diseño es genuinamente
bueno para un prototipo académico: paleta "Apple-style" cohesiva (un solo acento
azul, neutrales tintados, sin gradiente morado genérico de IA), tipografía con
escala consistente, gráficos SVG nativos con tooltips, crosshair, navegación por
teclado y live regions — nivel de pulido que sí impresiona en 60 segundos. Los
empty states tienen jerarquía clara y CTA accionable en vez de pantallas en
blanco. El accessibility groundwork (skip link, focus-visible, aria-live,
aria-label en gráficos, focus trap en el drawer móvil) está mejor que el
promedio de un proyecto estudiantil.

El problema real que puede arruinar la primera impresión es técnico, no visual:
el cliente HTTP tiene un **timeout de 5 segundos** (`frontend/src/api/client.js:23`)
mientras el contexto de la tarea indica un backend free-tier con cold-start de
30-50s. Si un reclutador prueba el login apenas se despierta el servicio, el
login **va a fallar por timeout antes de que el backend responda**, y el mensaje
de error que ve es "No pudimos iniciar sesión. Revisá tus credenciales y el
backend" — que le echa la culpa al usuario en vez de explicar que el servidor
está despertando. Eso es exactamente el escenario que la tarea pidió evaluar, y
tal como está el código, sí se ve como una app rota en el peor momento posible.

Aparte de eso, hay contraste insuficiente (AA) en el gris secundario usado para
casi todo el texto de apoyo del dashboard, y un empty state de error que muestra
"0" en todas las métricas sin dejar claro que son ceros por falla de conexión y
no datos reales.

## Hallazgos

| Severidad | Pantalla/Componente | Hallazgo | Sugerencia |
|---|---|---|---|
| HIGH | `frontend/src/api/client.js:23` | `timeout: 5000` en el cliente axios. Con un backend de cold-start ~30-50s (mencionado en el contexto de la tarea), el primer login o la primera carga del dashboard van a fallar por timeout antes de que el backend despierte. El error se atribuye a credenciales incorrectas, no a latencia del servidor. | Subir el timeout (o quitarlo) para el request de login/bootstrap específicamente, y detectar `error.code === "ECONNABORTED"` para mostrar un mensaje distinto: "El servidor está iniciando, esto puede tardar hasta 1 minuto. Reintentando..." con reintento automático. |
| MEDIUM | Global — `text-neutral-400` (`#86868b`) sobre fondo blanco | Contraste ≈3.6:1, por debajo de WCAG AA (4.5:1) para texto normal. Se usa como color de texto secundario en subtítulos de página (`LoginPage.jsx:70,80`, `DashboardPage.jsx:145`), labels de cards (`ResumenCards.jsx:61`), encabezados de tabla (`TablaEstadoEquipos.jsx:38-56`) y subtítulos de gráficos (`GraficoLineaBase.jsx:463`). Es prácticamente todo el texto de apoyo de la app. | Oscurecer el tono a algo como `neutral-500` (`#6e6e73`, ≈4.6:1) para texto de body/labels, y reservar `neutral-400` solo para texto decorativo o ≥18px. |
| MEDIUM | `DashboardPage.jsx:39,49,201-215` | Cuando falla el fetch inicial (sin datos previos), `isInitialLoading` pasa a `false` mientras `data` sigue `null`, así que `ResumenCards` renderiza con `resumenInicial` (todo en cero) al mismo tiempo que el banner de error dice "Se muestran los últimos datos válidos" — pero no hay datos válidos previos, son ceros. Para una cuenta demo recién creada esto es indistinguible de "0 alertas reales" vs. "no pudimos conectar". | Distinguir explícitamente el caso "sin datos por error" del caso "sin datos porque la cuenta está vacía": no renderizar `ResumenCards` con ceros cuando `error && !hasData`, mostrar un estado de error dedicado en su lugar. |
| LOW | `frontend/src/components/ui/Input.jsx:35` | `min-h-[38px]` en los inputs de login/formularios, por debajo del target táctil de 44px que sí se respeta en `Button.jsx` (`min-h-[44px]`, documentado ahí mismo como WCAG 2.2 AA). Inconsistencia dentro del propio sistema de diseño. | Igualar a `min-h-[44px]` en `Input` para consistencia y cumplimiento AA en mobile. |
| LOW | Global (no hay componente de "servidor despertando") | No existe ningún estado de UI para latencia larga de arranque — el skeleton (`Skeleton.jsx`) es indistinguible entre "cargando normal" y "esperando 40s a que el backend arranque". Combinado con el hallazgo HIGH de timeout, un reclutador no tiene ninguna señal de que debe esperar. | Agregar un mensaje que aparezca solo si la carga inicial supera ~5-8s ("Esto puede tardar un poco la primera vez"), independiente del fix de timeout. |
| LOW | `frontend/src/pages/LoginPage.jsx` | Buena base visual (card centrada, logo, jerarquía clara) pero no hay credenciales demo visibles ni un botón "Probar con cuenta demo" — un reclutador sin credenciales reales no puede completar el flujo de 60 segundos sin que alguien le pase un usuario/clave. | Si el objetivo es que un reclutador entre solo, considerar un botón de "Ingresar con cuenta demo" que autocomplete o loguee directamente. |

## Puntos fuertes a destacar (no requieren acción)

- `GraficoLineaBase.jsx`: gráfico SVG hecho a mano con curvas suavizadas, zonas de referencia, tooltip accesible (`role="tooltip"`), crosshair, navegación por teclado (flechas) y `aria-live` para lectores de pantalla. Nivel de detalle que no se ve en la mayoría de dashboards estudiantiles.
- `EmptyState.jsx` + su uso en `EquiposPage.jsx:169-178`: título, descripción y CTA accionable ("Registrar primer equipo") en vez de una tabla vacía sin contexto.
- Paleta y tipografía sin los anti-patrones típicos de IA genérica: sin gradiente morado/azul, un solo acento cromático, neutrales tintados en vez de gris puro, escala tipográfica con letter-spacing negativo consistente.
- Accesibilidad estructural presente desde el inicio: skip link (`Layout.jsx:48-53`), focus trap en el drawer del sidebar (`Sidebar.jsx:45-76`), `prefers-reduced-motion` respetado globalmente (`index.css:250-262`), touch targets de 44px documentados en `Button.jsx`.
