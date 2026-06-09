# Proceso de Onboarding para Piloto — ManttoAI

## 1. Visita Tecnica a Planta (Semana 1)

### 1.1 Preparacion Previa

Antes de la visita, el equipo de ManttoAI debe:

- Coordinar fecha y hora con el contacto principal de la empresa.
- Solicitar un plano simple o croquis de la planta indicando ubicacion de equipos.
- Confirmar disponibilidad de Wi-Fi en las areas donde se instalaran sensores.
- Preparar el kit de instalacion (3 sensores ESP32, repetidor Wi-Fi, cables, caja protectora).
- Revisar la lista de equipos criticos identificada en la fase Discovery.

### 1.2 Check de Instalacion

| Actividad | Responsable | Tiempo estimado |
|---|---|---|
| Revision del entorno y condiciones ambientales | Equipo ManttoAI | 30 min |
| Verificacion de cobertura Wi-Fi en puntos de instalacion | Equipo ManttoAI | 20 min |
| Montaje fisico de sensores en equipos seleccionados | Equipo ManttoAI + Tecnico cliente | 60 min por equipo |
| Conexion y prueba de transmision de datos | Equipo ManttoAI | 15 min por equipo |
| Validacion de datos en plataforma (dashboard) | Equipo ManttoAI + Cliente | 30 min |
| Firma de acta de instalacion | Ambos | 10 min |

### 1.3 Criterios de Ubicacion de Sensores

- **Temperatura**: A menos de 30 cm del componente critico (motor, rodamiento, superficie caliente). Evitar luz solar directa y corrientes de aire.
- **Humedad**: Misma logica que temperatura, en ambientes donde la humedad sea relevante (camaras de frio, invernaderos, bodegas).
- **Vibracion**: Montaje rigido sobre la carcasa del equipo, alineado con el eje del motor. Usar cinta de doble cara industrial o soporte mecanico.

### 1.4 Acta de Instalacion

Template minimo que debe quedar firmado por ambas partes:

```markdown
# Acta de Instalacion — Piloto ManttoAI

**Empresa**: [Nombre]
**Fecha**: [DD/MM/AAAA]
**Direccion**: [Direccion planta]
**Responsable ManttoAI**: [Nombre]
**Responsable Cliente**: [Nombre, Cargo]

## Equipos Instalados

| ID Sensor | Equipo monitoreado | Ubicacion | MAC address | Lecturas verificadas |
|---|---|---|---|---|
| SENSOR-01 | [Nombre equipo] | [Area] | AA:BB:CC:DD:EE:01 | Temp/Hum/Vib OK |
| SENSOR-02 | [Nombre equipo] | [Area] | AA:BB:CC:DD:EE:02 | Temp/Hum/Vib OK |
| SENSOR-03 | [Nombre equipo] | [Area] | AA:BB:CC:DD:EE:03 | Temp/Hum/Vib OK |

## Configuracion de Red

- SSID: [Nombre red Wi-Fi]
- Calidad de senal: [Buena / Regular / Con repetidor]
- Observaciones: ...

## Firmas

_________________________           _________________________
Equipo ManttoAI                       Cliente
```

---

## 2. Configuracion de Umbrales (Semana 2)

### 2.1 Metodologia

Los umbrales se configuran en una sesion de trabajo colaborativa con el cliente, usando los siguientes criterios:

#### Temperatura

| Tipo de equipo | Umbral alerta | Umbral critico | Accion |
|---|---|---|---|
| Motor electrico | > 80°C | > 95°C | Alerta temprana → Detencion programada |
| Compresor | > 100°C | > 120°C | Verificar refrigeracion → Parada |
| Bomba hidraulica | > 70°C | > 85°C | Revisar sellos y lubricacion |
| Camara de frio | < 2°C o > 8°C | < -2°C o > 12°C | Ajustar termostato → Perdida de producto |
| Invernadero | < 10°C o > 32°C | < 5°C o > 38°C | Activar calefaccion/ventilacion |

#### Humedad

| Tipo de equipo | Umbral alerta | Umbral critico | Accion |
|---|---|---|---|
| Camara de frio | > 75% HR | > 90% HR | Verificar sellos puertas |
| Equipo electronico | > 70% HR | > 85% HR | Riesgo de cortocircuito |
| Invernadero | < 40% o > 85% HR | < 25% o > 95% HR | Activar riego/ventilacion |
| Bodega producto seco | > 60% HR | > 75% HR | Riesgo de deterioro |

#### Vibracion (eje X, Y, Z)

| Tipo de equipo | Umbral alerta (mm/s) | Umbral critico (mm/s) | Accion |
|---|---|---|---|
| Motor < 50 HP | > 4.5 | > 7.1 | Balanceo / Cambio rodamientos |
| Motor 50-300 HP | > 4.5 | > 11.2 | Evaluacion estructural |
| Compresor alternativo | > 18.0 | > 28.0 | Mantenimiento de valvulas |
| Bomba centrifuga | > 5.0 | > 9.0 | Revision de impulsores |

> Referencia: ISO 10816-1 para vibracion en maquinaria industrial.

### 2.2 Proceso de Configuracion

1. Revisar historial de fallas del cliente (ultimos 12 meses).
2. Identificar los modos de falla mas frecuentes por equipo.
3. Configurar umbrales iniciales basados en la tabla referencial.
4. Activar monitoreo por 48 horas para capturar linea base.
5. Ajustar umbrales segun datos reales de operacion.
6. Validar con el cliente y confirmar en acta.

### 2.3 Acta de Configuracion de Umbrales

```markdown
# Acta de Configuracion de Umbrales

**Empresa**: [Nombre]
**Fecha**: [DD/MM/AAAA]

## Umbrales Configurados

| Equipo | Variable | Alerta | Critico | Accion automatica |
|---|---|---|---|---|
| [Equipo 1] | Temperatura | > 80°C | > 95°C | Notificacion email |
| [Equipo 1] | Vibracion X | > 4.5 mm/s | > 7.1 mm/s | Notificacion email + SMS |
| ... | ... | ... | ... | ... |

## Observaciones del Cliente
...

## Firmas
_________________________           _________________________
Equipo ManttoAI                       Cliente
```

---

## 3. Capacitacion de Usuarios (Semana 3)

### 3.1 Perfiles y Contenido

#### Tecnicos de Mantenimiento (2 horas)

| Modulo | Contenido | Duracion |
|---|---|---|
| Introduccion | Que es ManttoAI, que mide y por que es relevante | 20 min |
| Dashboard operativo | Visualizacion de lecturas en tiempo real, historial | 30 min |
| Alertas | Recepcion de notificaciones, interpretacion de alarmas | 25 min |
| Registro de acciones | Como documentar acciones tomadas ante una alerta | 20 min |
| Q&A | Preguntas y solucion de dudas | 25 min |

#### Supervisores / Jefes de Turno (1.5 horas)

| Modulo | Contenido | Duracion |
|---|---|---|
| Dashboard gerencial | Visibilidad de estado general de equipos | 20 min |
| Interpretacion de tendencias | Lectura de graficos, deteccion temprana | 30 min |
| Alertas y escalamiento | Protocolo ante alertas criticas | 20 min |
| Reportes | Descarga de reportes de periodo | 10 min |
| Q&A | Preguntas y solucion de dudas | 10 min |

#### Gerentes / C-Level (45 min)

| Modulo | Contenido | Duracion |
|---|---|---|
| Vision general | Impacto del monitoreo en continuidad operativa | 15 min |
| Indicadores | Tiempo de actividad, alertas resueltas, tendencias | 15 min |
| ROI | Casos de uso, proyeccion de ahorro | 10 min |
| Q&A | Preguntas estrategicas | 5 min |

### 3.2 Material de Capacitacion

Cada usuario recibe:

- **Guia rapida**: Tarjeta plastificada (10x15 cm) con pasos clave del dashboard.
- **Manual de usuario**: Documento PDF con capturas de pantalla y procedimientos.
- **Credenciales**: Usuario y contrasena de acceso a la plataforma.
- **Canal de soporte**: Numero de WhatsApp grupal para incidencias rapidas.

### 3.3 Checklist de Capacitacion

| Perfil | Capacitado | Fecha | Material entregado |
|---|---|---|---|
| Tecnico 1 | [ ] SI [ ] NO | | [ ] |
| Tecnico 2 | [ ] SI [ ] NO | | [ ] |
| Supervisor | [ ] SI [ ] NO | | [ ] |
| Gerente | [ ] SI [ ] NO | | [ ] |

---

## 4. Soporte Prioritario

### 4.1 Acuerdo de Nivel de Servicio (SLA)

| Tipo de incidencia | Tiempo de respuesta | Tiempo de resolucion | Canal |
|---|---|---|---|
| Plataforma caida | 1 hora | 4 horas | WhatsApp + Email |
| Sensor sin datos | 2 horas | 8 horas | WhatsApp |
| Alarma falsa recurrente | 4 horas | 24 horas | WhatsApp + Email |
| Duda de usuario | 4 horas | 48 horas | WhatsApp |
| Ajuste de umbrales | 4 horas | 72 horas | Email / Reunion |

### 4.2 Canales de Soporte

- **Grupo WhatsApp**: Canal primario. Cliente + Equipo ManttoAI. Respuesta en <2 horas en horario laboral (Lun-Vie 8:00-19:00).
- **Email**: soporte@manttoai.cl — Incidencias formales y seguimiento.
- **Reunion agendada**: Para temas que requieran pantalla compartida o visita a planta.
- **Dashboard de incidencias**: Tablero compartido con estado de cada incidencia abierta.

### 4.3 Procedimiento de Escalamiento

```
Incidencia reportada
    ↓
Respuesta inicial (<2h) → Clasificar: Baja / Media / Alta / Critica
    ↓
Resolucion N1 (ManttoAI): <24h
    ↓ (si no se resuelve)
Resolucion N2 (Sebastian Bravo - Backend/IoT): <48h
    ↓ (si no se resuelve)
Resolucion N3 (Angel Rubilar - Hardware/ML): <72h
    ↓
Cierre y documentacion
```

---

## 5. Reuniones Quincenales de Seguimiento

### 5.1 Estructura de la Reunion (30 min)

| Tiempo | Tema | Responsable |
|---|---|---|
| 5 min | Estado general del sistema | Equipo ManttoAI |
| 10 min | Alertas detectadas y acciones tomadas | Cliente |
| 5 min | Tendencias y patrones observados | Equipo ManttoAI |
| 5 min | Proximos pasos y ajustes | Ambos |
| 5 min | Dudas y feedback abierto | Cliente |

### 5.2 Minuta Template

```markdown
# Minuta de Seguimiento — Piloto ManttoAI

**Empresa**: [Nombre]
**Fecha**: [DD/MM/AAAA]
**Asistentes**: [Nombres]

## Estado del Sistema
- Sensores operativos: [X/3]
- Alertas activas: [X]
- Alertas resueltas desde ultima reunion: [X]
- Tiempo de actividad: [XX]%

## Alertas Detectadas
| Equipo | Variable | Valor | Fecha | Accion tomada |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Tendencias
- [Observacion sobre temperatura, humedad o vibracion]
- [Patron recurrente identificado]

## Proximos Pasos
- [Accion 1 — Responsable — Fecha]
- [Accion 2 — Responsable — Fecha]

## Comentarios del Cliente
- ...

## Proxima Reunion
[Fecha y hora]
```
