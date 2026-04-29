# 15. Plan de Gestión de Calidad

Define **cómo** ManttoAI Predictivo asegura y controla la calidad del producto y los procesos durante todo el ciclo de vida. Complementa a [Métricas de Calidad](./16-metricas-calidad.md) y al [Reporte de Control de Calidad](./17-reporte-control-calidad.md).

---

## 1. Política de calidad

> *"Ningún cambio llega a `main` sin que esté probado, revisado y trazable. La calidad es responsabilidad de todo el equipo, no de una persona."*

Estándares de referencia:
- **ISO/IEC 25010** — modelo de calidad de producto de software.
- **PMBOK 6ª ed.** — área de conocimiento de Calidad.

---

## 2. Dimensiones de calidad evaluadas (ISO/IEC 25010)

| Dimensión | Atributo evaluado | Cómo se mide |
|-----------|------------------|--------------|
| **Functional Suitability** | Modelo ML cumple objetivo de negocio | F1-Score y Accuracy ≥ 80% |
| **Reliability** | Sistema disponible y reproducible | Despliegue Docker inmutable, uptime, suite Pytest |
| **Performance Efficiency** | API responde rápido | Latencia < 500 ms en endpoints clave |
| **Maintainability** | Código limpio, testeable | Cobertura ≥ 70%, 0 lint warnings |
| **Usability** | UI utilizable por usuario académico | Manual + flujos E2E Playwright |
| **Security** | Auth y secretos protegidos | JWT, `.env` fuera de git, dependencias auditadas |

Métricas concretas y umbrales: ver [Métricas de Calidad](./16-metricas-calidad.md).

---

## 3. Roles y responsabilidades

| Rol | Persona | Responsabilidad |
|-----|---------|----------------|
| Responsable de Calidad | Sebastián Bravo | Custodia el plan, gestiona CI/CD, aprueba merges a `main`. |
| Revisor par (Backend) | Sebastián / Ángel | Code review de PRs de FastAPI, ML, MQTT. |
| Revisor par (Frontend) | Luis | Code review de PRs de React, Tailwind, integraciones. |
| Responsable QA Manual | Luis | Ejecuta checklist de demo y prueba de aceptación de hitos. |
| Equipo completo | Los tres | Cumple Definition of Done antes de marcar tarea cerrada. |

> **Regla:** ningún integrante aprueba su propio PR. Mínimo 1 revisor par.

---

## 4. Aseguramiento de calidad (QA — proceso preventivo)

QA actúa **antes** de que el defecto llegue a `main`. Se ejecuta en cada cambio.

### 4.1 Flujo de Pull Request

```
Issue (vinculada a actividad del Gantt)
        │
        ▼
Branch feature/* o fix/* desde main
        │
        ▼
Commits Conventional Commits (feat:, fix:, refactor:)
        │
        ▼
Pull Request abierto
        │
        ├──► GitHub Actions ejecuta automáticamente:
        │     • ruff check (lint backend)
        │     • black --check (formato backend)
        │     • pytest --cov=app (tests + cobertura)
        │     • npm run lint (lint frontend)
        │     • npm run build (verifica bundle)
        │     • playwright test (E2E si aplica)
        │
        ├──► Revisor par revisa código (mínimo 1)
        │
        ▼
Si todo verde + 1 aprobación → merge a main
Si algo falla → vuelve al autor; no se mergea
```

### 4.2 Checklist obligatorio del autor antes de pedir review

- [ ] La rama parte de `main` actualizada
- [ ] Commits siguen Conventional Commits
- [ ] Tests añadidos/actualizados para el cambio
- [ ] `pytest` local pasa
- [ ] `ruff` y `black` no reportan warnings
- [ ] Si toca UI: probado manualmente en `http://localhost:5173`
- [ ] Si toca API: probado con `curl` o Postman
- [ ] Documentación actualizada si cambia comportamiento público
- [ ] PR vinculado a Issue con ID del Gantt

### 4.3 Auditoría asistida por IA
Los PRs no triviales se revisan adicionalmente con el agente `code-reviewer` (Claude Code). El output se adjunta como comentario al PR. La aprobación humana sigue siendo obligatoria.

---

## 5. Control de calidad (QC — proceso de verificación)

QC verifica que el producto cumple los criterios **después** de construido. Se ejecuta por hito.

### 5.1 Gates por hito

Cada hito del [archivo de hitos](../cronograma/11-hitos-proyecto.md) tiene un **gate** que debe pasar para considerarse cerrado:

| Hito | Gate de calidad | Aprobador |
|------|----------------|-----------|
| Backend API Core | Pytest > 70% cobertura, todos los endpoints documentados | Sebastián |
| Modelo ML entrenado | F1-Score ≥ 80% en validación cruzada estratificada | Ángel |
| Dashboard MVP | 5+ flujos Playwright verdes, manual visual | Luis |
| Integración MQTT | Mensaje publicado → registro en BD < 2s | Sebastián |
| CI/CD | Pipeline verde 3 ejecuciones consecutivas | Sebastián |
| Deployment VPS | Smoke test (`scripts/smoke_test.sh`) en producción | Sebastián |
| Entrega Final | Reporte ISO/IEC 25010 firmado por equipo | Equipo |

### 5.2 Definition of Done (DoD) — universal por tarea

Una tarea se considera **terminada** solo si cumple TODO lo siguiente:

1. Código mergeado en `main`.
2. Tests automatizados pasando (no `xfail`, no `skip` injustificado).
3. Documentación tocada si aplica.
4. Issue del board GitHub Projects movida a `Done`.
5. Hoja `Control Semanal` del Gantt actualizada.

### 5.3 Auditoría continua
- **Diaria automática:** GitHub Actions corre suite completa en cada push.
- **Semanal manual:** Responsable QA Manual ejecuta `bash scripts/smoke_test.sh` contra el entorno de desarrollo.
- **Por hito:** Revisión cruzada de métricas vs umbrales en la hoja `Control Semanal`.

---

## 6. Manejo de no conformidades

Cuando una métrica cae bajo el umbral o un test rompe:

1. **Detección:** CI falla o auditoría manual lo reporta.
2. **Bloqueo:** No se mergea ningún PR adicional al área afectada hasta resolver.
3. **Diagnóstico:** El responsable del módulo identifica causa raíz (no solo el síntoma).
4. **Corrección:** Se abre fix branch, se corrige, se añade test de regresión.
5. **Verificación:** El revisor par valida que el problema no se repite.
6. **Documentación:** Si la no conformidad fue significativa, se registra en [Lecciones Aprendidas](../gestion-proyecto/03-registro-lecciones-aprendidas.md).

---

## 7. Mejora continua

- **Retrospectiva por sprint** (cada 2 semanas): qué funcionó, qué no, qué cambia. Acta en el [Plan de Reuniones](../comunicaciones/23-plan-reuniones.md).
- **Indicadores de proceso** revisados al cierre del proyecto: tasa de PRs rechazados, tiempo promedio de review, defectos detectados post-merge.
- **Actualización del plan** si una métrica resulta poco útil o demasiado laxa.
