# 12. Plan de Gestión de Costos — ManttoAI

**Asignatura:** Gestión de Proyectos
**Evaluación 3 — Trabajo en clases (30%)**
**Grupo 4 — Área de Conocimiento PMBOK:** Gestión de los Costos del Proyecto (PMBOK 6ta Edición, Capítulo 7)
**Proyecto aplicado:** ManttoAI — Plataforma de Monitoreo IoT por Rubro
**Integrantes:** Sebastián Bravo · Luis Loyola · Ángel Rubilar
**Temuco, mayo de 2026**

---

## 1. Marco Teórico — Gestión de los Costos según PMBOK 6ta Edición

La Gestión de los Costos del Proyecto incluye los procesos involucrados en planificar, estimar, presupuestar, financiar, gestionar y controlar los costos, de modo que el proyecto se complete dentro del presupuesto aprobado (PMI, 2017). Se compone de **cuatro procesos**, distribuidos entre los grupos de Planificación y Monitoreo y Control:

| # | Proceso | Grupo de procesos | Propósito |
|---|---|---|---|
| 7.1 | Planificar la Gestión de los Costos | Planificación | Definir cómo se estimarán, presupuestarán, gestionarán y controlarán los costos. |
| 7.2 | Estimar los Costos | Planificación | Desarrollar una aproximación de los recursos monetarios necesarios. |
| 7.3 | Determinar el Presupuesto | Planificación | Sumar los costos estimados para establecer la línea base de costos. |
| 7.4 | Controlar los Costos | Monitoreo y Control | Monitorear el estado del proyecto, actualizar costos y gestionar cambios a la línea base. |

**Conceptos clave aplicados:** Costos directos e indirectos, costos fijos y variables, contingencia, reserva de gestión, EVM (Earned Value Management) con CV, SV, CPI y SPI, estimación análoga, paramétrica, ascendente y por tres valores (PERT).

---

## 2. Aplicación al Proyecto ManttoAI

### 2.1 Plan de Gestión de Costos (Proceso 7.1)

ManttoAI opera bajo un capital inicial acotado de **$3.000.000 CLP** aportado en partes iguales por los tres socios fundadores ($1.000.000 c/u). El plan establece:

- **Moneda y unidad de medida:** Pesos chilenos (CLP); USD convertido a tipo de cambio referencial $800/USD.
- **Niveles de precisión:** estimaciones redondeadas a $1.000 CLP; presupuesto agregado a $10.000 CLP.
- **Umbrales de control:** desviaciones > 10% sobre línea base requieren aprobación del directorio (los 3 socios).
- **Reglas EVM:** seguimiento mensual con CPI objetivo ≥ 0,95.
- **Formatos de reporte:** planilla mensual de ejecución revisada por el contador externo (contadoresenlinea.cl).

### 2.2 Estimar los Costos (Proceso 7.2)

Se aplica **estimación ascendente (bottom-up)** para activos físicos y digitales, y **estimación análoga** para honorarios profesionales (referencia: contadoresenlinea.cl, abogados externos por servicio).

**Inversión inicial Año 1:**

| Categoría | Detalle | Monto (CLP) |
|---|---|---|
| Equipamiento físico | 6 kits ESP32 (industrial, agrícola, comercial) + cableado | $165.000 |
| Infraestructura digital anual | Droplet 2GB, PostgreSQL gestionada, Spaces 250GB, dominio .cl | $327.600 |
| **Total activos Año 1** | | **$492.600** |

**Costos operacionales mensuales Año 1 (sin retiro de socios):**

| Ítem | Monto mensual (CLP) |
|---|---|
| Infraestructura Digital Ocean (São Paulo) | $25.600 |
| Contador externo (contadoresenlinea.cl, IVA incl.) | $89.000 |
| Abogado externo (3 servicios/año prorrateado) | $62.500 |
| Domicilio comercial virtual (OficinVirtual.cl) | $5.000 |
| Dominio y herramientas digitales | $5.000 |
| **Total mensual** | **$187.100** |
| **Total anual** | **$2.245.200** |

### 2.3 Determinar el Presupuesto (Proceso 7.3)

La línea base de costos se construye sumando: estimaciones de actividades + reservas de contingencia (riesgos identificados) + reserva de gestión (riesgos no identificados).

| Componente | Monto (CLP) | % del capital |
|---|---|---|
| Activos Año 1 (línea base) | $492.600 | 16,4% |
| Operación 12 meses (línea base) | $2.245.200 | — |
| Reserva de contingencia (10% ingresos por suscripción mensual una vez activos) | Variable | — |
| Reserva de gestión (saldo del capital) | $2.507.400 | 83,6% |
| **Capital comprometido total** | **$3.000.000** | **100%** |

> Con $187.100/mes en costos fijos y $3.000.000 de capital, el presupuesto cubre **~16 meses de operación sin ingresos**, holgura suficiente para validar el modelo comercial. La reserva de contingencia del 10% sobre ingresos por suscripción se activa desde el primer cliente (Mecanismo 2 del fondo de contingencia).

### 2.4 Controlar los Costos (Proceso 7.4)

Se aplica **Gestión del Valor Ganado (EVM)** con corte mensual a cargo del CEO/Comercial (Luis Loyola) y validación del contador externo. Indicadores monitoreados:

| Indicador | Fórmula | Umbral de alerta |
|---|---|---|
| Variación de Costos (CV) | EV − AC | CV < 0 por 2 meses consecutivos |
| Índice de Desempeño de Costos (CPI) | EV / AC | CPI < 0,95 |
| Estimación a la Conclusión (EAC) | BAC / CPI | EAC > BAC × 1,10 |
| Variación del Cronograma (SV) | EV − PV | SV < 0 |

**Acciones correctivas predefinidas:**

1. Desviación 5–10%: revisión interna del directorio, ajuste de gastos discrecionales (capacitaciones, herramientas digitales).
2. Desviación 10–20%: postergación de incorporación de equipos propios (Año 2) y uso de reserva de gestión.
3. Desviación > 20%: revisión del modelo de precios y plan de captación; eventual rebaja de retiros proyectados (Año 2: $300.000 → $200.000 brutos por socio).

**Hitos de control de costos por etapa:**

| Etapa | Clientes activos | Ingreso mensual suscripción | Utilidad neta anual proyectada |
|---|---|---|---|
| Año 1 — Validación | 0 – 4 | $0 – $352.000 | Negativa (cubierta por reserva) |
| Año 2 — Crecimiento | 10 – 12 | $880.000 – $1.056.000 | ~$1.034.800 |
| Año 3 — Consolidación | 20 – 22 | $1.760.000 – $1.936.000 | ~$1.952.000 |

---

## 3. Conclusión

La aplicación de los cuatro procesos del Área de Conocimiento de Costos al proyecto ManttoAI permite establecer una línea base presupuestaria realista de **$3.000.000 CLP** con una estructura de costos operacionales acotada de **$187.100 CLP mensuales**, generando una autonomía financiera de aproximadamente 16 meses sin ingresos. La estimación ascendente, soportada en cotizaciones reales (Digital Ocean, NIC Chile, contadoresenlinea.cl, OficinVirtual.cl), entrega un nivel de precisión adecuado para una microempresa en etapa de validación. El control de costos mediante EVM, con umbrales de CPI ≥ 0,95 y acciones correctivas escalonadas, permite gestionar las desviaciones antes de que comprometan la viabilidad del proyecto. La separación entre línea base de costos y reserva de gestión (83,6% del capital) constituye el principal mecanismo de mitigación financiera frente a la incertidumbre comercial propia de los primeros meses de operación.

---

## 4. Costos del Prototipo Académico (referencia)

El prototipo técnico implementado en este repositorio tuvo un costo real de **USD $98** (hardware ESP32 + VPS), muy por debajo del presupuesto académico simulado de CLP $9.790.000. El plan de negocios aquí presentado corresponde a la proyección comercial de ManttoAI como empresa real y es el entregable de la Evaluación 3 (Gestión de Costos).

---

## Referencias

- Project Management Institute. (2017). *Guía de los Fundamentos para la Dirección de Proyectos (Guía del PMBOK®) — Sexta Edición*. PMI.
- Digital Ocean. (2026). *Pricing — Droplets, Managed Databases, Spaces*. https://www.digitalocean.com/pricing
- contadoresenlinea.cl. (2026). *Planes de contabilidad para microempresas*. https://www.contadoresenlinea.cl/
- NIC Chile. (2026). *Aranceles y registro de dominios .cl*. https://www.nic.cl/
- OficinVirtual.cl. (2026). *Servicio de domicilio tributario y comercial — Temuco*. https://oficinvirtual.cl/
