# 09. Plan de Gestión del Cronograma

Este documento define **cómo se planifica, monitorea y controla** el cronograma de ManttoAI Predictivo durante el ciclo académico (Enero–Junio 2025). Complementa al archivo Gantt operativo `docs/office/Cronograma_ManttoAI.xlsx` y a la [Lista de Actividades](./10-lista-actividades.md).

---

## 1. Metodología

Enfoque **híbrido**: marco predictivo PMBOK 6ª ed. para planificación e hitos académicos, combinado con prácticas ágiles (sprints quincenales) para la ejecución técnica.

| Elemento | Definición |
|----------|------------|
| Unidad de planificación | Sprint de 2 semanas |
| Unidad de control | Semana calendario (Lunes a Domingo) |
| Línea base | Hoja `Cronograma Gantt` del archivo `Cronograma_ManttoAI.xlsx` |
| Línea de seguimiento | Hoja `Control Semanal` del mismo archivo |

---

## 2. Herramientas de gestión

| Herramienta | Uso |
|-------------|-----|
| **MS Excel — `Cronograma_ManttoAI.xlsx`** | Línea base Gantt, control semanal de avance, registro de variaciones. |
| **GitHub Projects (Kanban)** | Tablero operativo de tareas: `Backlog → In Progress → Review → Done`. |
| **GitHub Issues / PRs** | Trazabilidad de actividades técnicas; cada PR cierra una o más Issues vinculadas a un ID del Gantt. |
| **Discord** | Coordinación sincrónica semanal (ver [Plan de Reuniones](../comunicaciones/23-plan-reuniones.md)). |

---

## 3. Roles y responsabilidades

| Rol | Persona | Responsabilidad sobre el cronograma |
|-----|---------|-------------------------------------|
| Director de Proyecto | Sebastián Bravo | Custodia la línea base; aprueba cambios; consolida el control semanal. |
| Líder Técnico | Ángel Rubilar | Reporta avance de actividades de hardware/ML. |
| Líder de Producto | Luis Loyola | Reporta avance de actividades de frontend/BD/documentación. |
| Equipo completo | Los tres | Actualiza su % de avance real **antes** de la reunión semanal. |

---

## 4. Ritual de control semanal

### Cadencia
Toda semana se ejecuta el siguiente ciclo:

| Día | Hito | Quién |
|-----|------|-------|
| **Domingo (hasta 22:00)** | Cada integrante actualiza su % real en la hoja `Control Semanal`. | Cada miembro |
| **Lunes 20:00–21:00** | Reunión de control de cronograma (ver [Plan de Reuniones](../comunicaciones/23-plan-reuniones.md)). | Equipo completo |
| **Lunes (post-reunión)** | Director consolida cambios, congela snapshot semanal y publica resumen en Discord. | Sebastián Bravo |

### Métricas del control semanal
La hoja `Control Semanal` registra por actividad:

- Fecha inicio planificada vs real
- Fecha fin planificada vs real
- % Plan vs % Real
- **Variación en días** (`Fin Real − Fin Plan`)

### Indicadores agregados (KPI)

| Indicador | Fórmula | Umbral verde | Umbral amarillo | Umbral rojo |
|-----------|---------|--------------|------------------|-------------|
| **SPI** (Schedule Performance Index) | `% Real / % Plan` | ≥ 0.95 | 0.85–0.94 | < 0.85 |
| **Variación máxima** (días) | `max(Variación)` por sprint | ≤ 2 días | 3–4 días | ≥ 5 días |
| **Actividades en rojo** | Cuenta de `Variación ≥ 5` | 0 | 1 | ≥ 2 |

---

## 5. Protocolo de desvíos

### 5.1 Clasificación
- **Verde:** Avance dentro del plan. Se documenta y continúa.
- **Amarillo:** Desvío leve (1–4 días). Se registra causa y se ajusta esfuerzo del sprint.
- **Rojo:** Desvío crítico (≥ 5 días) o bloqueo de cadena de dependencias. Se activa plan de contingencia.

### 5.2 Plan de contingencia (cuando aparece rojo)
1. **Identificar:** En la reunión semanal, se nombra la actividad y el responsable.
2. **Diagnosticar:** ¿Causa técnica, dependencia, alcance, esfuerzo?
3. **Reaccionar:** Aplicar la primera estrategia viable de la siguiente lista:
   - **Mockear dependencia** (ej. simulador IoT desbloquea frontend si MQTT atrasa).
   - **Reducir alcance** del sprint manteniendo el hito (DoD mínimo viable).
   - **Reasignar carga** entre integrantes.
   - **Reprogramar hito** solo como último recurso, con aprobación del Director.
4. **Registrar:** Anotar decisión en el [Registro de Lecciones Aprendidas](../gestion-proyecto/03-registro-lecciones-aprendidas.md) y, si afecta línea base, en el flujo de Control de Cambios del [Plan de Dirección](../gestion-proyecto/02-plan-direccion-proyecto.md).

### 5.3 Ejemplo histórico
Semana 8 — `Diseño de arquitectura del sistema` cerró con +7 días de variación. Acción aplicada: paralelizar diseño detallado con inicio temprano de FastAPI (Sebastián), evitando bloquear el sprint siguiente. Documentado en lecciones aprendidas.

---

## 6. Control de cambios al cronograma

Modificar la **línea base** (fechas planificadas, hitos, alcance del Gantt) requiere:

1. Solicitud escrita en GitHub Issue con etiqueta `cronograma:change-request`.
2. Análisis de impacto: tiempo, costo, calidad, riesgos.
3. Aprobación del Director de Proyecto.
4. Actualización de la hoja `Cronograma Gantt` y registro de la versión anterior como histórico.
5. Comunicación al equipo en la siguiente reunión semanal.

Cambios menores (% de avance, fechas reales, notas operativas) **no** requieren control de cambios formal.

---

## 7. Cierre del cronograma

Al cerrar el proyecto:
- Variación final consolidada por hito.
- SPI promedio del proyecto.
- Lecciones aprendidas sobre estimación.
- Archivo del `Cronograma_ManttoAI.xlsx` versionado en `docs/office/`.
