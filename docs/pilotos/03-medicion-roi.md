# Medicion de ROI y Metricas de Exito — Piloto ManttoAI

## 1. Metricas de Exito del Piloto

### 1.1 Metricas Operativas

| Metrica | Definicion | Formula | Target |
|---|---|---|---|
| Disponibilidad del sistema | % de tiempo que la plataforma recibe datos sin interrupcion | (Tiempo operativo / Tiempo total) x 100 | >= 95% |
| Precision de alertas | % de alertas confirmadas por el cliente como validas | (Alertas validas / Total alertas) x 100 | >= 70% |
| Tiempo medio de deteccion | Tiempo entre ocurrencia del evento y alerta generada | Suma(tiempos) / N eventos | < 5 min |
| Sensores activos | % de sensores transmitiendo datos correctamente | (Sensores activos / Total instalados) x 100 | >= 90% |
| Alertas por equipo/semana | Promedio de alertas generadas por equipo monitoreado | Total alertas / (N equipos x N semanas) | Segun linea base |

### 1.2 Metricas de Adopcion

| Metrica | Definicion | Target |
|---|---|---|
| Usuarios activos semanales | % de usuarios que acceden al dashboard al menos 1 vez por semana | >= 80% |
| Acciones post-alerta | % de alertas que generan una accion documentada | >= 60% |
| Satisfaccion (NPS) | Net Promoter Score al cierre del piloto | >= 40 |
| Tiempo de respuesta a incidencia | Tiempo promedio entre reporte y primera respuesta | < 2 horas |
| Concurrencia a reuniones | % de reuniones quincenales con asistencia del cliente | >= 80% |

### 1.3 Metricas de Impacto de Negocio

| Metrica | Definicion | Metodo de calculo |
|---|---|---|
| Paradas no planificadas | Reduccion de paradas no programadas durante el piloto | Comparacion con historial del cliente (12 meses previos) |
| Tiempo de inactividad evitado | Horas de operacion recuperadas por deteccion temprana | Suma de horas de parada evitada segun alertas |
| Costos de mantenimiento | Variacion en costos de manten correctivo vs. preventivo | Reporte del cliente pre y post piloto |
| Vida util extendida | Estimacion de extension de vida util de equipos monitoreados | Proyeccion basada en reduccion de estres operativo |

---

## 2. Calculo de ROI

### 2.1 Formula General

```
ROI (%) = ((Beneficio total - Costo total) / Costo total) x 100
```

### 2.2 Componentes del Beneficio

#### Paradas Evitadas

```
Paradas_evitadas = N_alertas_criticas x %_alertas_confirmadas x horas_parada_promedio
Costo_parada_evitada = Paradas_evitadas x Costo_hora_parada
```

Donde:
- **N_alertas_criticas**: Numero de alertas criticas durante el piloto.
- **%_alertas_confirmadas**: Proporcion de alertas que el cliente valida como riesgo real.
- **horas_parada_promedio**: Estimacion del cliente sobre duracion tipica de una parada correctiva (incluye diagnostico, repuestos, reparacion, puesta en marcha).
- **Costo_hora_parada**: Costo por hora de equipo detenido (perdida de produccion + mano de obra ociosa + costos fijos asignados).

**Ejemplo practico**:

```
N_alertas_criticas = 12
%_alertas_confirmadas = 75%
horas_parada_promedio = 4 horas
Costo_hora_parada = $120.000 CLP

Paradas_evitadas = 12 x 0.75 x 4 = 36 horas
Costo_parada_evitada = 36 x $120.000 = $4.320.000 CLP
```

#### Costos de Mantenimiento Evitados

```
Manto_correctivo_evitado = (N_alertas x Costo_intervencion_promedio) x %_alertas_evitaron_falla
```

**Ejemplo practico**:

```
N_alertas = 12
Costo_intervencion_promedio = $80.000 CLP (incluye repuestos menores)
%_alertas_evitaron_falla = 50%

Ahorro = 12 x $80.000 x 0.50 = $480.000 CLP
```

#### Extension de Vida Util

```
Valor_extension = (Valor_equipo / Vida_util_anos) x Anos_extension_estimados
```

### 2.3 Componentes del Costo

Para el piloto, el costo para la empresa es **$0**. Sin embargo, para la proyeccion de ROI post-piloto:

| Concepto | Valor mensual | Anual |
|---|---|---|
| Suscripcion ManttoAI | $88.000 CLP | $1.056.000 CLP |
| Kit sensores (3 unidades, cada 3 anos) | $11.250 CLP | $135.000 CLP amortizado |
| Capacitacion anual | $5.000 CLP | $60.000 CLP |
| **Total anual estimado** | | **$1.251.000 CLP** |

### 2.4 Proyeccion de ROI Post-Piloto

Usando los ejemplos anteriores:

```
Costo_anual_solucion = $1.251.000 CLP
Beneficio_anual_estimado = $4.320.000 + $480.000 = $4.800.000 CLP

ROI = (($4.800.000 - $1.251.000) / $1.251.000) x 100 = 284%
```

> Esto significa que por cada $1 CLP invertido en ManttoAI, la empresa recupera $3.84 CLP en ahorros.

---

## 3. Template de Caso de Uso Documentado

```markdown
# Caso de Uso: [Nombre Empresa]

**Sector**: [Industrial / Agricola / Comercial]
**Rubro especifico**: [Ej: Procesamiento de alimentos / Cultivo de tomates / Logistica]
**Tamano empresa**: [XX empleados]
**Ubicacion**: [Ciudad, Region]

## Perfil del Cliente
[Breve descripcion de la empresa, su operacion principal y los desafios que enfrentaban antes del piloto]

## Problema
[Descripcion del problema especifico que ManttoAI ayudo a resolver]

### Antes de ManttoAI
- [Situacion anterior: paradas frecuentes, mantenimiento reactivo, etc.]
- [Cuantificacion del problema: X paradas al mes, Y horas de inactividad, $Z en perdidas]

## Solucion
[Descripcion de la implementacion: equipos monitoreados, sensores instalados, configuracion]

### Equipos Monitoreados
| Equipo | Sensor | Variables |
|---|---|---|
| [Motor principal] | ESP32-01 | Temperatura, Vibracion |
| [Compresor] | ESP32-02 | Temperatura, Humedad |
| [Camara de frio] | ESP32-03 | Temperatura, Humedad |

## Resultados

| Variable | Antes | Durante piloto | Mejora |
|---|---|---|---|
| Paradas no planificadas/mes | X | Y | -XX% |
| Tiempo deteccion de fallas | X horas | Y minutos | -XX% |
| Alertas tempranas generadas | N/A | XX | Nuevo |
| Costo estimado de paradas evitadas/mes | N/A | $XX CLP | Nuevo |

### Testimonio del Cliente
> "[Cita textual del contacto principal de la empresa]"
> — [Nombre], [Cargo]

### Lecciones Aprendidas
1. [Leccion 1]
2. [Leccion 2]
3. [Leccion 3]

## Proximos Pasos
- [Opcion 1: Expansion a mas equipos]
- [Opcion 2: Contratacion de suscripcion]
- [Opcion 3: Integracion con otros sistemas]

---
*Caso de uso documentado por ManttoAI — [Fecha]*
*Confidencialidad: [Datos sensibles anonimizados con autorizacion del cliente]*
```

---

## 4. Template de Testimonio de Cliente

```markdown
# Testimonio — [Nombre Empresa]

**Nombre del firmante**: [Nombre completo]
**Cargo**: [Cargo]
**Empresa**: [Nombre]
**Rubro**: [Sector]

## Preguntas

### 1. ?Cual era el principal desafio que enfrentaban antes de usar ManttoAI?
[Respuesta del cliente]

### 2. ?Que lo motivo a participar en el programa piloto?
[Respuesta del cliente]

### 3. ?Como describiria su experiencia durante el piloto?
[Respuesta del cliente]

### 4. ?Que resultados concretos observo?
[Respuesta del cliente]

### 5. ?Recomendaria ManttoAI a otras empresas? ?Por que?
[Respuesta del cliente]

### 6. En una palabra, ?como definiria ManttoAI?
[Respuesta del cliente]

## Autorizacion de Uso

Autorizo a ManttoAI a utilizar mi nombre, cargo y las respuestas anteriores con fines
comerciales y de marketing, incluyendo sitio web, redes sociales y material promocional.

[ ] Deseo que mi testimonio sea anonimizado (sin nombre ni empresa visibles)

_________________________           _________________________
Firma Cliente                         Fecha

_________________________
Firma ManttoAI
```

---

## 5. Encuesta NPS (Net Promoter Score)

### Pregunta Principal

> **En una escala del 0 al 10, ?que tan probable es que recomiende ManttoAI a un colega o empresa del mismo rubro?**
>
> 0 = Nada probable | 5 = Neutral | 10 = Extremadamente probable

### Clasificacion

| Puntaje | Categoria | Significado |
|---|---|---|
| 9-10 | Promotores | Clientes leales que recomendaran ManttoAI |
| 7-8 | Pasivos | Clientes satisfechos pero no entusiastas |
| 0-6 | Detractores | Clientes insatisfechos que pueden danar la reputacion |

### Formula

```
NPS = %Promotores - %Detractores
```

Rango: -100 a +100. Target piloto: >= 40.

### Preguntas de Seguimiento (Solo para detractores y pasivos)

1. ?Que fue lo que menos le gusto de la experiencia?
2. ?Que funcionalidad considera que falta o deberia mejorar?
3. ?Hubo algun problema recurrente que afecto su experiencia?

### Preguntas de Seguimiento (Solo para promotores)

1. ?Que fue lo que mas valoro de ManttoAI?
2. ?Hay alguna funcionalidad adicional que le gustaria tener?
3. ?Nos autoriza a contactarlo para obtener un testimonio formal?

### Preguntas Adicionales (Todos los encuestados)

4. ?Que tan facil fue usar la plataforma? (1 = Muy dificil, 5 = Muy facil)
5. ?La instalacion de sensores interrumpio su operacion normal? (SI / NO / Parcialmente)
6. ?Considera que el soporte recibido fue oportuno? (SI / NO / Parcialmente)
7. ?Recomendaria cambios en el proceso de onboarding? (Texto libre)

### Plantilla de Encuesta

```markdown
# Encuesta de Satisfaccion — Programa Piloto ManttoAI

**Empresa**: [Nombre]
**Encuestado**: [Nombre, Cargo]
**Fecha**: [DD/MM/AAAA]

## NPS

?Que tan probable es que recomiende ManttoAI?
[0] [1] [2] [3] [4] [5] [6] [7] [8] [9] [10]

## Preguntas Adicionales

?Que tan facil fue usar la plataforma?
[1] Muy dificil  [2] Dificil  [3] Neutral  [4] Facil  [5] Muy facil

?La instalacion interrumpio la operacion?
[ ] SI  [ ] NO  [ ] Parcialmente

?El soporte fue oportuno?
[ ] SI  [ ] NO  [ ] Parcialmente

?Que mejoraria?
...
```

---

## 6. Propuesta de Contrato Post-Piloto

### 6.1 Estructura de la Propuesta

```markdown
# Propuesta Comercial — ManttoAI

**Para**: [Nombre Empresa]
**Fecha**: [DD/MM/AAAA]
**Valido hasta**: [DD/MM/AAAA]

## Plan de Suscripcion

| Concepto | Detalle |
|---|---|
| Plan | [Industrial / Agricola / Comercial] |
| Equipos monitoreados | Hasta 5 |
| Sensores incluidos | 5 unidades ESP32 |
| Soporte | Prioridad alta, respuesta < 2 horas |
| Capacitacion | 2 sesiones anuales |
| Reportes | Mensuales + Anual con analisis ML |

## Precios

| Item | Valor mensual | Valor anual (descuento 2 meses) |
|---|---|---|
| Suscripcion estandar | $88.000 CLP | $880.000 CLP |
| Descuento post-piloto (20%) | -$17.600 CLP | -$176.000 CLP |
| **Total post-piloto** | **$70.400 CLP** | **$704.000 CLP** |
| Incluye kit sensores (por cuenta de ManttoAI) | $0 | $0 |

## Proximo Paso: Onboarding sin Friccion

1. Firma de contrato.
2. Activacion de suscripcion (los sensores ya estan instalados).
3. Continuidad inmediata del monitoreo.
4. Facturacion: inicio al mes siguiente de la firma.

## Vigencia

Oferta valida por 30 dias desde la fecha de cierre del piloto.
```

### 6.2 Argumentos de Cierre

| Objecion | Respuesta |
|---|---|
| "No tenemos presupuesto ahora" | El piloto ya demostro un ROI de 284%. La inversion de $70.400 CLP/mes se cubre con menos de 1 hora de parada evitada al mes. |
| "Necesitamos evaluarlo internamente" | Entendemos. Podemos agendar una presentacion con su equipo directivo para resolver dudas. ?Quien mas deberia participar? |
| "Los sensores se quedan igual" | Correcto, no hay necesidad de reinstalar. La transicion es inmediata y sin interrupcion del monitoreo. |
| "No vimos resultados suficientes" | Revisemos juntos los datos. Podemos extender el periodo de evaluacion por 1 mes adicional sin costo para confirmar el valor. |
| "Queremos comparar con otras opciones" | Valoramos que evaluen alternativas. Lo importante es que los sensores ya estan instalados y funcionando. Mantener la continuidad tiene valor en si mismo. |
