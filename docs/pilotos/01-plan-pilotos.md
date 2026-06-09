# Plan de Pilotos — Estrategia de Seleccion y Proceso

## 1. Estrategia de Seleccion de Empresas

### Perfil de Empresa Ideal

| Criterio | Rango optimo | Justificacion |
|---|---|---|
| Tamano | 30-200 empleados | Suficiente capacidad operativa sin burocracia excesiva |
| Facturacion anual | $500M - $5.000M CLP | Presupuesto disponible para soluciones IoT post-piloto |
| Sector | Industrial, agricola o comercial | Rubros definidos en el alcance del producto |
| Equipos criticos | 3-10 equipos monitoreables | Suficientes para validar sin abrumar la capacidad del piloto |
| Decision tecnologico | CTO, Jefe de Mantenimiento o Gerente de Operaciones | Interlocutor con capacidad de decision |
| Madurez digital | Media | Procesos documentados pero sin soluciones IoT previas |

### Criterios de Exclusion

- Empresas con solucion IoT activa contratada (no aplica si estan en etapa de evaluacion)
- Menos de 15 empleados (capacidad de pago limitada)
- Mas de 500 empleados (ciclos de decision demasiado largos para un piloto academico)
- Sectores regulados que requieran certificaciones especiales (mineria, salud, energia)
- Empresas sin persona tecnica dedicada o sin acceso a Wi-Fi en las instalaciones

### Matriz de Puntaje de Seleccion

| Criterio | Peso | 1 punto | 2 puntos | 3 puntos |
|---|---|---|---|---|
| Tamano empresa | 15% | <30 o >200 emp. | 30-80 o 150-200 emp. | 80-150 empleados |
| Sector | 20% | No prioritario | Sector compatible | Rubro exacto del producto |
| Equipos criticos | 20% | <3 equipos | 3-5 equipos | 6-10 equipos |
| Acceso a Wi-Fi | 15% | Sin Wi-Fi | Wi-Fi limitado | Wi-Fi estable en planta |
| Interlocutor tecnologico | 15% | Sin interlocutor tecnico | Jefe de turno | CTO / Jefe de Manto. |
| Urgencia percibida | 15% | Sin urgencia | Interes general | Problema activo de paradas |

**Puntaje minimo para admision**: 60/100.

---

## 2. Canales de Outreach

### 2.1 LinkedIn (prioritario)

- **Perfil objetivo**: CTOs, Jefes de Mantenimiento, Gerentes de Operaciones, Gerentes de Planta.
- **Estrategia**: Conexion con mensaje personalizado destacando el programa gratuito. Seguimiento a los 3 dias si no hay respuesta.
- **Contenido**: Publicaciones semanales en el perfil de ManttoAI mostrando resultados del piloto (anonimizados), datos del sector y casos de uso.

### 2.2 Redes de Contactos

- **Contactos directos del equipo**: Ex empleadores, practicas profesionales, proveedores actuales.
- **Incubadoras / Aceleradoras**: Contacto con startups industriales que puedan referir clientes.
- **Exalumnos INACAP**: Red de egresados en posiciones de liderazgo tecnico en la industria.

### 2.3 Asociaciones Industriales

- SOFOFA (Sociedad de Fomento Fabril)
- ASIQUIM (Asociacion de Industrias Quimicas)
- CHILEALIMENTOS (Asociacion de Industrias de Alimentos)
- SNA (Sociedad Nacional de Agricultura)
- Camaras de Comercio regionales
- Corfo — Programas de innovacion y transformacion digital

### 2.4 Ferias y Eventos

- EXPOMIN (mineria — alcance limitado pero networking valioso)
- EXPOMACH (maquinaria y equipo industrial)
- FISA (Feria Industrial de Santiago)
- Eventos Corfo de transformacion digital para PYMEs

---

## 3. Proceso de 5 Fases

### Fase 1: Outreach (Mes 1)

**Objetivo**: Identificar y contactar 20+ empresas candidatas.

**Actividades**:
- Semana 1-2: Mapeo de empresas por rubro y region. Construccion de lista priorizada de 30 empresas.
- Semana 2-3: Envio de emails personalizados (ver [04-materiales-venta.md](./04-materiales-venta.md)). Conexiones en LinkedIn.
- Semana 3-4: Llamadas de discovery para primeras 10 empresas interesadas.
- **Meta**: 5 empresas pasan a evaluacion detallada.

**Entregables**:
- Lista priorizada de 30 empresas
- 10 discovery calls agendadas
- Pipeline documentado en spreadsheet

### Fase 2: Discovery (Semanas 3-4)

**Objetivo**: Evaluar idoneidad tecnica y comercial de cada candidato.

**Actividades**:
- Discovery call de 45 min siguiendo metodologia SPICED (ver [04-materiales-venta.md](./04-materiales-venta.md))
- Evaluacion tecnica remota: infraestructura Wi-Fi, equipos a monitorear, condiciones ambientales
- Visita a planta (opcional, solo para candidatos con alto puntaje)
- Scoring segun matriz de seleccion

**Entregables**:
- Reporte de evaluacion por empresa
- Matriz de puntaje completada
- 3 empresas seleccionadas (mas 2 en lista de espera)

**Criterio de decision**: Las 3 empresas con mayor puntaje en la matriz de seleccion, sujeto a disponibilidad para comenzar onboarding en el Mes 2.

### Fase 3: Onboarding (Mes 2)

**Objetivo**: Instalar sensores y capacitar usuarios.

**Actividades** (detalle completo en [02-onboarding-piloto.md](./02-onboarding-piloto.md)):
- Semana 1: Visita tecnica a planta. Instalacion de sensores ESP32 en equipos criticos.
- Semana 2: Configuracion de umbrales con el cliente. Validacion de datos en plataforma.
- Semana 3: Capacitacion de usuarios (tecnicos, supervisores, gerentes).
- Semana 4: Periodo de estabilizacion. Monitoreo intensivo y ajustes.

**Entregables**:
- Acta de instalacion firmada
- Umbrales configurados y validados
- 3 capacitaciones realizadas por empresa
- Checklist de onboarding completado

### Fase 4: Operacion (Meses 3-5)

**Objetivo**: Operacion continua con soporte prioritario y seguimiento quincenal.

**Actividades**:
- Monitoreo continuo de datos y alertas
- Reuniones quincenales de seguimiento (30 min):
  - Semana 1-2: Resultados iniciales, ajustes de umbrales
  - Semana 3-4: Tendencias, alertas detectadas, primeras metricas
  - Semana 5-6: Evaluacion de impacto, problemas de equipos detectados
  - Semana 7-8: Proyecciones ML, resultados parciales
  - Semana 9-10: Preparacion de cierre, recoleccion de testimonios
  - Semana 11-12: Presentacion de resultados finales
- Soporte con respuesta en <4 horas habiles
- Registro de incidencias y resolucion

**Entregables**:
- Dashboard de monitoreo activo
- Minutas de reuniones quincenales
- Registro de incidencias atendidas
- Datos de telemetria completos del periodo

### Fase 5: Cierre (Mes 6)

**Objetivo**: Presentar resultados, medir satisfaccion y cerrar conversion comercial.

**Actividades**:
- Semana 1: Preparacion de reporte individual por empresa
- Semana 2: Reunion de cierre con cada empresa. Presentacion de resultados y ROI.
- Semana 3: Encuesta NPS. Solicitud de testimonio formal y caso de uso documentado.
- Semana 4: Entrega de propuesta comercial con descuento post-piloto.

**Entregables**:
- Reporte de impacto por empresa
- 3 casos de uso documentados
- 1+ testimonio formal firmado
- Encuesta NPS completada
- 2+ propuestas comerciales entregadas

---

## 4. Timeline Consolidado (6 Meses)

```
Mes 1     | Outreach ████████████████░░░░░░░░░░░░░░░░░░░░░░░░ |
Mes 2     | Onboard ░░░░░░░░░░░░░░████████████████░░░░░░░░░░░░ |
Mes 3-5   | Operacion ░░░░░░░░░░░░░░░░░░░░████████████████████ |
Mes 6     | Cierre ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████████ |
         Sem 1  Sem 2  Sem 3  Sem 4  Sem 5  Sem 6  Sem 7  Sem 8 ...
```

### Hitos Clave

| Hito | Fecha estimada | Criterio de exito |
|---|---|---|
| 30 empresas contactadas | Semana 2 | Registro en CRM / spreadsheet |
| 10 discovery calls | Semana 4 | Minutas de llamada |
| 3 empresas seleccionadas | Semana 4 | Contrato de piloto firmado |
| Instalacion completa | Semana 6 | Acta de instalacion |
| Capacitacion finalizada | Semana 8 | Checklists completados |
| 1er mes de operacion | Semana 12 | Sin interrupciones >4h |
| Reporte de cierre | Semana 24 | Entregado y presentado |
| Propuesta comercial | Semana 24 | Entregada a cada empresa |

---

## 5. Riesgos del Programa

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Empresa se retira antes de completar piloto | Media | Alto | Contrato de piloto con clausula de compromiso minimo de 2 meses |
| Problemas de conectividad Wi-Fi en planta | Alta | Medio | Kit con repetidor Wi-Fi incluido. Evaluacion de red en discovery |
| Rotacion de personal clave en la empresa | Baja | Alto | Capacitar a 2+ personas por empresa. Documentar procesos |
| Datos insuficientes para modelo ML | Media | Bajo | Generar datos sinteticos complementarios si es necesario |
| Fuga de informacion confidencial de la empresa | Baja | Critico | Acuerdo de confidencialidad firmado. Datos anonimizados en reportes publicos |

---

## 6. Presupuesto del Programa

| Concepto | Costo unitario | Cantidad | Total |
|---|---|---|---|
| Kit ESP32 (3 sensores + repetidor) | $45.000 CLP | 3 empresas | $135.000 CLP |
| Hosting VPS (3 meses adicionales) | $20.000 CLP/mes | 3 meses | $60.000 CLP |
| Traslado para instalacion (3 visitas) | $30.000 CLP | 3 empresas | $90.000 CLP |
| Material de capacitacion impreso | $10.000 CLP | 3 empresas | $30.000 CLP |
| **Total programa** | | | **$315.000 CLP** |

> Costos cubiertos por el capital inicial de $3.000.000 CLP. El programa piloto representa ~10.5% del presupuesto total disponible.
