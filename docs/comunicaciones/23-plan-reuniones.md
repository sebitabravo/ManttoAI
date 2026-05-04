# 23. Plan de Reuniones y Gestión de Tareas

Define **cuándo, dónde, quién, cómo** se coordina el equipo de ManttoAI y **cómo se gestionan las tareas** del día a día. Complementa al [Plan de Comunicaciones](./21-plan-gestion-comunicaciones.md) y a la [Matriz de Comunicaciones](./22-matriz-comunicaciones.md).

---

## 1. Cadencia de reuniones

| Reunión | Frecuencia | Día y hora (CLT) | Duración | Canal |
|---------|------------|------------------|----------|-------|
| **Daily asíncrono** | Diaria (lun–vie) | Antes de las 12:00 | 5 min | Discord — canal `#daily` |
| **Weekly de control** | Semanal | **Lunes 20:00–21:00** | 60 min | Discord — sala `#weekly-call` |
| **Sprint Planning** | Cada 2 semanas (lun) | Lunes 20:00–21:30 (reemplaza Weekly) | 90 min | Discord — sala `#weekly-call` |
| **Retrospectiva** | Cada 2 semanas (vie) | **Viernes 19:00–20:00** | 60 min | Discord — sala `#retro` |
| **Reunión de hito** | Por hito | Convocada por Director | 60–90 min | Discord o presencial INACAP |
| **Demo ad-hoc** | Bajo demanda | Convocada con 24 h | 30 min | Discord — sala `#demo` |

> Toda reunión sincrónica se confirma 24 h antes en `#general`. Si un integrante no puede asistir, deja su update por escrito antes del inicio.

---

## 2. Roles en cada reunión

| Rol | Responsabilidad | Asignación por defecto |
|-----|----------------|------------------------|
| **Facilitador / Director** | Abre, cierra, controla agenda y tiempo, modera. | Sebastián Bravo |
| **Minutero** | Toma notas, publica acta en `docs/office/minutas/`. | Rotativo (ver tabla rotación) |
| **Time-keeper** | Avisa cuando se exceden los bloques de tiempo. | El Facilitador, salvo delegación. |
| **Asistentes** | Llegan preparados con su update y bloqueos identificados. | Todo el equipo |

### Rotación de minutero

| Sprint | Minutero |
|--------|----------|
| Impar (1, 3, 5…) | Luis Loyola |
| Par (2, 4, 6…)   | Ángel Rubilar |
| Reunión de cierre | Sebastián Bravo |

---

## 3. Agenda tipo por reunión

### 3.1 Daily asíncrono (5 min, escrito)
Cada integrante publica en `#daily` con el formato:

```
Ayer:    [qué cerré]
Hoy:     [qué voy a hacer]
Bloqueo: [si hay]
```

### 3.2 Weekly de control (60 min)
| Bloque | Tiempo | Contenido |
|--------|--------|-----------|
| Apertura | 5 min | Saludo + objetivos de la reunión |
| Avance Gantt | 15 min | Cada integrante reporta % real vs plan; se actualiza hoja `Control Semanal` en vivo |
| Indicadores QA | 10 min | Estado de CI, cobertura, alertas técnicas |
| Bloqueos y riesgos | 15 min | Identificación y plan de acción |
| Compromisos próxima semana | 10 min | Asignación clara con fecha y responsable |
| Cierre y minuta | 5 min | Lectura rápida de acuerdos, confirmación |

### 3.3 Sprint Planning (90 min, cada 2 lunes)
1. Revisión del sprint anterior — 15 min
2. Selección de tareas del backlog — 30 min
3. Estimación y asignación — 25 min
4. Definición de hito del sprint — 10 min
5. Confirmación en GitHub Projects — 10 min

### 3.4 Retrospectiva (60 min, cada 2 viernes)
Formato **Start / Stop / Continue**:
- ¿Qué empezamos a hacer? (Start)
- ¿Qué dejamos de hacer? (Stop)
- ¿Qué seguimos haciendo? (Continue)

Acción: máximo 3 mejoras concretas para el siguiente sprint, con responsable.

### 3.5 Reunión de hito
- Demo del entregable
- Verificación de gate de calidad (ver [Plan de Calidad §5.1](../calidad/15-plan-gestion-calidad.md))
- Aprobación o rechazo
- Firma del cierre del hito en acta

---

## 4. Plantilla de minuta

Toda reunión sincrónica genera una minuta en `docs/office/minutas/YYYY-MM-DD-tipo.md` con esta estructura:

```markdown
# Minuta — [Tipo de Reunión]
**Fecha:** YYYY-MM-DD
**Hora:** HH:MM – HH:MM
**Lugar/Canal:** Discord #weekly-call
**Facilitador:** [Nombre]
**Minutero:** [Nombre]
**Asistentes:** [Lista]
**Ausentes:** [Lista + motivo]

## 1. Agenda
1. ...
2. ...

## 2. Avance reportado
- [Integrante]: [% real / actividades / bloqueos]

## 3. Acuerdos
| # | Acuerdo | Responsable | Fecha límite |
|---|---------|-------------|--------------|
| 1 | ...     | ...         | ...          |

## 4. Riesgos y bloqueos identificados
- ...

## 5. Próxima reunión
- Fecha, hora, agenda preliminar
```

Las minutas se versionan en git. El minutero las publica **dentro de las 24 h** posteriores a la reunión.

---

## 5. Gestión de tareas — flujo paso a paso

### 5.1 Tablero
Se usa **GitHub Projects (Kanban)** vinculado al repositorio. Columnas:

```
📥 Backlog   →   🎯 Sprint   →   🔄 In Progress   →   👀 Review   →   ✅ Done
```

### 5.2 Ciclo de vida de una tarea

| Paso | Acción | Quién | Cuándo |
|------|--------|-------|--------|
| 1 | Crear Issue en GitHub vinculada a un ID del Gantt | Quien la identifica | Al detectar necesidad |
| 2 | Etiquetar (`backend`, `frontend`, `ml`, `infra`, `docs`) y asignar prioridad (P0/P1/P2) | Director | Antes del Sprint Planning |
| 3 | Mover de `Backlog` a `Sprint` con responsable y estimación | Equipo en Planning | Sprint Planning |
| 4 | Mover a `In Progress` al empezar | Responsable | Cuando inicia trabajo |
| 5 | Crear branch `feature/issue-NN-slug` o `fix/issue-NN-slug` | Responsable | Al iniciar código |
| 6 | Abrir PR cuando esté lista; mover Issue a `Review` | Responsable | Al estar lista |
| 7 | Revisor par aprueba o pide cambios (ver [Plan de Calidad §4](../calidad/15-plan-gestion-calidad.md)) | Revisor | Dentro de 24 h hábiles |
| 8 | Mergear a `main`; mover Issue a `Done`; actualizar Gantt | Responsable | Tras aprobación |

### 5.3 Reglas del tablero
- Una persona no tiene más de **2 tareas en `In Progress`** simultáneas.
- Tarea bloqueada → etiqueta `blocked` + comentario explicando bloqueo + se reporta en próximo daily.
- Tarea sin movimiento por 5 días → se revisa en Weekly.
- Definition of Done es la del [Plan de Calidad §5.2](../calidad/15-plan-gestion-calidad.md).

### 5.4 Priorización
| Etiqueta | Significado | Acción |
|----------|-------------|--------|
| **P0 — Crítica** | Bloquea hito o producción | Se atiende antes de cualquier otra |
| **P1 — Alta** | Requerida en sprint actual | Se completa en sprint actual |
| **P2 — Normal** | Importante pero diferible | Se planifica para próximo sprint |
| **P3 — Mejora** | Deseable, no urgente | Backlog |

---

## 6. Comunicación entre reuniones

| Situación | Canal | SLA de respuesta |
|-----------|-------|------------------|
| Bloqueo técnico urgente | Discord `@aquí` | < 2 h en horario hábil |
| Pregunta no urgente | Discord `#general` | < 24 h |
| Decisión de arquitectura | GitHub Discussions | Asíncrono, mín. 2 votos |
| Pull Request | GitHub | Review < 24 h hábiles |
| Reporte de hito | Plataforma INACAP | Según calendario académico |

---

## 7. Trazabilidad

Toda decisión relevante deja rastro en al menos uno de estos lugares:

- **Minutas** (`docs/office/minutas/`) — decisiones de reunión.
- **GitHub Issues / PRs** — decisiones técnicas.
- **`docs/decisiones/`** — Architecture Decision Records (ADR) para cambios estructurales.
- **[Lecciones Aprendidas](../gestion-proyecto/03-registro-lecciones-aprendidas.md)** — aprendizajes del equipo.
