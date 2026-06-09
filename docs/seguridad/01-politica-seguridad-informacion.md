# Politica de Seguridad de la Informacion

- **Version:** 1.0
- **Fecha:** 2026-06-09
- **Clasificacion:** Uso interno / Confidencial
- **Aprobado por:** Director de Proyecto — ManttoAI
- **Proxima revision:** 2026-09-09 (trimestral)

---

## 1. Proposito

Establecer el marco de gobierno para la seguridad de la informacion en la plataforma ManttoAI, definiendo los principios, objetivos, roles y responsabilidades que garantizan la proteccion de la confidencialidad, integridad y disponibilidad de los activos de informacion.

## 2. Alcance

Esta politica aplica a:

- **Toda la informacion** procesada, almacenada o transmitida por la plataforma ManttoAI, incluyendo telemetria IoT, datos de equipos, configuraciones de usuarios y registros de operacion.
- **Todos los sistemas, aplicaciones e infraestructura** que soportan la plataforma: servidores, bases de datos, dispositivos IoT, red y endpoints.
- **Todas las personas** con acceso a los sistemas de ManttoAI: empleados, contratistas, proveedores y usuarios autorizados.
- **Todas las ubicaciones** donde se procese o almacene informacion de ManttoAI: VPS, estaciones de trabajo de desarrollo y dispositivos de prueba.

Quedan **excluidos** del alcance los dispositivos ESP32 en campo mas alla del firmware provisto por ManttoAI, y los sistemas de terceros utilizados por clientes para acceder al dashboard.

## 3. Objetivos de Seguridad

| Objetivo | Descripcion | KPIs |
|---|---|---|
| **Confidencialidad** | Garantizar que la informacion solo sea accesible por personas autorizadas | 0 incidentes de fuga de datos; 100% de comunicaciones cifradas |
| **Integridad** | Asegurar que los datos de telemetria no sean alterados indebidamente | Auditoria de cambios; verificacion de checksums en backups |
| **Disponibilidad** | Mantener la plataforma operativa segun los SLAs definidos | Uptime >= 99.5%; RTO <= 4h; RPO <= 24h |
| **Cumplimiento** | Cumplir con requisitos legales (Ley 19.628) y contractuales | Auditorias anuales sin hallazgos criticos |

## 4. Roles y Responsabilidades

### 4.1 Director de Proyecto (CISO funcional)

- Responsable ultimo de la seguridad de la informacion en ManttoAI
- Aprueba politicas de seguridad y asigna recursos para su implementacion
- Lidera la respuesta a incidentes de seguridad mayores
- Revisa trimestralmente el estado del SGSI

### 4.2 Lider de Desarrollo (Backend/Frontend)

- Implementa controles de seguridad en el ciclo de desarrollo
- Realiza code review obligatorio antes de cada merge
- Mantiene las dependencias actualizadas y libres de vulnerabilidades conocidas
- Reporta incidentes de seguridad al Director de Proyecto

### 4.3 Lider de Infraestructura (Ops)

- Administra la configuracion segura del VPS, Docker Compose y red
- Ejecuta los procedimientos de backup y recuperacion
- Monitorea logs y alertas de seguridad
- Mantiene el inventario de activos actualizado

### 4.4 Lider de Hardware/ML

- Asegura la integridad del firmware en dispositivos ESP32
- Valida la calidad y seguridad de los datos del modelo ML
- Reporta anomalias en lecturas de sensores

### 4.5 Usuarios del Sistema

- Usar las credenciales de acceso de forma responsable
- No compartir cuentas ni contraseñas
- Reportar inmediatamente cualquier actividad sospechosa
- Cumplir con las politicas de seguridad establecidas

## 5. Clasificacion de Activos de Informacion

### 5.1 Niveles de clasificacion

| Nivel | Descripcion | Ejemplos |
|---|---|---|
| **Publico** | Informacion que puede ser divulgada sin restriccion | Documentacion del producto, README publico, landing page |
| **Interno** | Informacion de uso interno del equipo ManttoAI | Documentos de proyecto, manuales, configuraciones de desarrollo |
| **Confidencial** | Informacion sensible cuyo acceso debe ser controlado | Datos de clientes, claves API, configuracion de produccion, logs de auditoria |
| **Restringido** | Informacion critica con el mas alto nivel de proteccion | Credenciales de acceso a infraestructura, secretos de aplicacion, datos personales (Ley 19.628) |

### 5.2 Inventario de activos principales

| Activo | Tipo | Clasificacion | Responsable |
|---|---|---|---|
| Base de datos MySQL (telemetria, equipos, usuarios) | Datos | Confidencial | Ops |
| Credenciales JWT y claves HMAC | Criptografico | Restringido | Backend |
| Credenciales MQTT (Mosquitto) | Criptografico | Restringido | Ops |
| Codigo fuente del backend | Software | Confidencial | Backend |
| Codigo fuente del frontend | Software | Confidencial | Frontend |
| Firmware ESP32 | Software | Interno | Hardware |
| Modelo ML (Random Forest) | Datos/Software | Interno | ML |
| Configuracion Docker Compose | Software | Confidencial | Ops |
| Certificados SSL/TLS | Criptografico | Restringido | Ops |
| Logs de aplicacion | Datos | Confidencial | Backend/Ops |
| Documentacion de proyecto | Datos | Interno | Director |
| Plan de negocios y costos | Datos | Confidencial | Director |

### 5.3 Tratamiento por nivel

| Nivel | Almacenamiento | Transmision | Retencion | Disposicion |
|---|---|---|---|---|
| Publico | Sin restriccion | Sin cifrado requerido | Indefinida | N/A |
| Interno | Repositorio privado | HTTPS | Vigencia del proyecto | Destruccion segura |
| Confidencial | Cifrado en reposo | HTTPS/TLS | 2 anos post-proyecto | Destruccion segura (DBAN/shred) |
| Restringido | Cifrado AES-256 | TLS 1.3+ | Vigencia del servicio + 1 ano | Destruccion fisica/criptografica |

## 6. Gestion de Incidentes de Seguridad

### 6.1 Definicion de incidente

Cualquier evento que comprometa o amenace la confidencialidad, integridad o disponibilidad de los activos de informacion, incluyendo:

- Acceso no autorizado a sistemas o datos
- Fuga o exposicion de informacion confidencial
- Ataque de denegacion de servicio (DoS/DDoS)
- Infectacion por malware
- Perdida o corrupcion de datos
- Intrusion fisica o logica en la infraestructura
- Falla de seguridad en dependencias de terceros

### 6.2 Severidad

| Nivel | Descripcion | Tiempo de respuesta |
|---|---|---|
| **P0 — Critico** | Exposicion de datos restringidos, indisponibilidad total del sistema | 30 minutos |
| **P1 — Alto** | Acceso no autorizado a datos confidenciales, funcionalidad critica afectada | 2 horas |
| **P2 — Medio** | Vulnerabilidad conocida sin exploit activo, degradacion de servicio | 8 horas |
| **P3 — Bajo** | Alerta de seguridad no confirmada, sospecha sin evidencia | 24 horas |

### 6.3 Flujo de respuesta

```
1. DETECCION
   - Automatizada: alertas de monitoreo, SAST, dependency scan
   - Manual: reporte de usuario, hallazgo en code review

2. CLASIFICACION
   - Evaluar severidad (P0-P3)
   - Notificar al Director de Proyecto (P0/P1 inmediato)
   - Asignar responsable de respuesta

3. CONTENCION
   - Aislar sistemas afectados (desconectar VPS, revocar accesos)
   - Preservar evidencia para analisis forense
   - Aplicar parche temporal si existe

4. ERRADICACION
   - Identificar causa raiz
   - Aplicar parche definitivo
   - Verificar que no queden rastros del incidente

5. RECUPERACION
   - Restaurar desde backup si es necesario
   - Reintegrar sistemas a produccion
   - Monitorear por recurrencia

6. LECCIONES APRENDIDAS
   - Documentar el incidente (formulario post-mortem)
   - Actualizar procedimientos y controles
   - Compartir hallazgos con el equipo (sin datos sensibles)
```

### 6.4 Canales de reporte

| Tipo | Canal | Contacto |
|---|---|---|
| Incidente de seguridad | Email + llamada (P0/P1) | director@manttoai.cl |
| Vulnerabilidad reportada por externos | Email con cifrado | security@manttoai.cl |
| Sospecha de violacion de politica | Reporte anonimo interno | Canal interno Slack/Teams |

## 7. Gestion de la Continuidad

### 7.1 Plan de Continuidad del Negocio (BCP)

El BCP de ManttoAI se activa cuando:

- El VPS principal no esta disponible por mas de 1 hora
- Se declara un desastre (incendio, inundacion, ataque fisico al datacenter)
- Una vulnerabilidad critica fuerza la desconexion del sistema

**Estrategia:** Restauracion en un VPS secundario (Digital Ocean u otro proveedor) desde el backup mas reciente. Tiempo estimado de restauracion: 4 horas (RTO).

### 7.2 Plan de Recuperacion ante Desastres (DRP)

| Paso | Accion | Responsable | Tiempo estimado |
|---|---|---|---|
| 1 | Declarar desastre y notificar al equipo | Director | 15 min |
| 2 | Provisionar VPS secundario | Ops | 30 min |
| 3 | Restaurar base de datos desde backup cifrado | Ops | 60 min |
| 4 | Desplegar contenedores Docker | Ops | 30 min |
| 5 | Validar integridad de datos | Backend | 30 min |
| 6 | Verificar conectividad MQTT y API | Backend/Ops | 30 min |
| 7 | Redirigir DNS al VPS secundario | Ops | 15 min |
| 8 | Comunicar restauracion a stakeholders | Director | 15 min |

## 8. Revision y Mejora Continua

### 8.1 Ciclo de revision

| Actividad | Frecuencia | Responsable |
|---|---|---|
| Revision de politicas de seguridad | Trimestral | Director de Proyecto |
| Auditoria de accesos y privilegios | Trimestral | Ops / Director |
| Prueba de restore de backups | Trimestral | Ops |
| Escaneo de vulnerabilidades (SAST) | Cada commit / Semanal | Backend |
| Dependency scanning | Semanal / Pre-merge | Backend |
| Revision de logs y monitoreo | Semanal | Ops |
| Auditoria interna SGSI | Anual | Director |
| Evaluacion de riesgos | Anual | Equipo completo |

### 8.2 Indicadores de desempeno (KPIs de seguridad)

| KPI | Objetivo | Medido |
|---|---|---|
| Tiempo medio de deteccion (MTTD) | < 2 horas para P0/P1 | Trimestral |
| Tiempo medio de respuesta (MTTR) | < 4 horas para P0/P1 | Trimestral |
| % de dependencias sin vulnerabilidades conocidas | >= 95% | Semanal |
| % de controles implementados vs. planificados | >= 90% | Trimestral |
| Uptime de la plataforma | >= 99.5% | Mensual |
| Incidentes P0/P1 por mes | 0 | Mensual |

### 8.3 No conformidades y acciones correctivas

Toda no conformidad detectada (auditoria, incidente, hallazgo) debe:

1. Registrarse en el registro de no conformidades
2. Analizarse para determinar causa raiz
3. Definir accion correctiva con responsable y plazo
4. Verificar la efectividad de la accion implementada
5. Actualizar la documentacion relevante

## 9. Sanciones por Incumplimiento

El incumplimiento de esta politica puede resultar en:

- Advertencia verbal o escrita (incumplimiento menor)
- Revision de privilegios de acceso (incumplimiento recurrente)
- Desvinculacion del proyecto (incumplimiento grave)
- Acciones legales en caso de violacion de la Ley 19.628

## 10. Documentos Relacionados

- [02-politica-control-acceso.md](./02-politica-control-acceso.md) — Control de acceso y privilegios
- [03-politica-backup-recuperacion.md](./03-politica-backup-recuperacion.md) — Backup y recuperacion
- [04-politica-desarrollo-seguro.md](./04-politica-desarrollo-seguro.md) — Desarrollo seguro
- [05-roadmap-certificacion.md](./05-roadmap-certificacion.md) — Roadmap de certificacion
- [00-gap-assessment.md](./00-gap-assessment.md) — Evaluacion de brecha

## Control de Cambios

| Version | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-06-09 | Version inicial | Director de Proyecto |

---

> Documento generado en el contexto del proyecto academico ManttoAI — INACAP.
> Proyecto: Plataforma de Monitoreo IoT por Rubro.
