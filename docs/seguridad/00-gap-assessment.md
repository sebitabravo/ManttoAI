# Evaluacion de Brecha (Gap Assessment) — ISO 27001 y SOC 2 Type I

- **Version:** 1.0
- **Fecha:** 2026-06-09
- **Clasificacion:** Uso interno / Confidencial
- **Responsable:** Director de Proyecto — ManttoAI

## Resumen Ejecutivo

Este documento presenta la evaluacion de brecha (gap assessment) de ManttoAI contra los estandares **ISO/IEC 27001:2022** y **SOC 2 Type I** (Trust Services Criteria). Se evaluaron 24 controles agrupados en 6 dominios. El resultado general muestra un **cumplimiento parcial del 37.5%**, con 9 controles implementados, 11 ausentes y 4 parciales.

Las brechas mas significativas se concentran en **gestion de incidentes**, **continuidad del negocio**, **cifrado de datos en reposo** y **auditoria de accesos privilegiados**. Estas deben priorizarse en el plan de remediacion (Fase 2 del roadmap).

## Metodologia

La evaluacion se realizo mediante:

1. **Revision de documentacion existente** — politicas, procedimientos y configuraciones actuales del proyecto
2. **Entrevistas con el equipo** — Sebastian Bravo (backend/ops), Luis Loyola (frontend/DB), Angel Rubilar (hardware/ML)
3. **Inspeccion tecnica** — revision del codigo fuente, configuracion de infraestructura (Docker Compose, Nginx, Mosquitto, MySQL), pipeline CI/CD y practicas de desarrollo
4. **Analisis contra la matriz de controles** —对照 ISO 27001 Anexo A (93 controles, 4 dominios) y SOC 2 TSC (Security, Availability, Confidentiality)

Cada control se clasifica como:

| Estado | Descripcion |
|---|---|
| **Cumple** | El control existe formalmente y esta documentado |
| **Parcial** | El control existe de forma informal o incompleta |
| **No cumple** | El control no existe o no esta implementado |

---

## ISO 27001 — Evaluacion de Brecha

### A.5 — Politicas de Seguridad de la Informacion

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.5.1 — Politicas de SI | No cumple | No existe politica formal documentada | Crear politica SGSI (doc 01) |
| A.5.2 — Revision de politicas | No cumple | No hay proceso de revision | Definir ciclo de revision anual |

### A.6 — Organizacion de la Seguridad de la Informacion

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.6.1 — Roles y responsabilidades | Parcial | Roles definidos informalmente en equipo | Formalizar matriz RACI |
| A.6.2 — Segregacion de tareas | Parcial | Backend/frontend separados por rol | Documentar segregacion |
| A.6.3 — Contacto con autoridades | No cumple | No definido | Crear procedimiento de contacto |
| A.6.4 — Contacto con grupos de interes | No cumple | No definido | Crear procedimiento |

### A.8 — Gestion de Activos

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.8.1 — Inventario de activos | Cumple | Repositorio documenta componentes, servicios y activos de hardware | Mantener actualizado |
| A.8.2 — Clasificacion de la informacion | No cumple | No hay esquema de clasificacion | Definir niveles de clasificacion |
| A.8.3 — Gestion de soportes | Parcial | Backups en VPS sin politicas formales | Crear politica de backups (doc 03) |

### A.9 — Control de Acceso

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.9.1 — Requisitos de negocio para control de acceso | Cumple | JWT auth, roles (admin/tecnico/visualizador) implementados | Documentar formalmente (doc 02) |
| A.9.2 — Gestion de acceso de usuarios | Parcial | Onboarding manual, no hay offboarding formal | Crear procedimiento de onboarding/offboarding (doc 02) |
| A.9.3 — Responsabilidades de usuarios | No cumple | No hay politica de uso aceptable | Definir AUP |
| A.9.4 — Control de acceso a sistemas y aplicaciones | Cumple | FastAPI con autenticacion, Nginx como proxy reverso | Revisar periodicamente |

### A.10 — Criptografia

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.10.1 — Controles criptograficos | No cumple | No hay cifrado en reposo en MySQL; HTTPS via Let's Encrypt implementado | Implementar cifrado de datos en reposo |
| A.10.2 — Gestion de claves | No cumple | No hay procedimiento de gestion de claves | Definir ciclo de vida de claves |

### A.11 — Seguridad Fisica y del Entorno

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.11.1 — Perimetros de seguridad fisica | Cumple | VPS en Ubuntu 22.04, firewall UFW, solo puertos 80/443/1883 expuestos | Verificar hardening periodico |
| A.11.2 — Equipos | Cumple | Acceso SSH por clave, Docker aislado, no hay equipos fisicos locales | Mantener configuracion |

### A.12 — Seguridad de las Operaciones

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.12.1 — Procedimientos operacionales | Parcial | Docker Compose como unico procedimiento documentado | Crear runbooks operacionales |
| A.12.2 — Proteccion contra malware | Cumple | Sin dependencias de riesgo conocidas, contenedores minimos | Mantener escaneo periodico |
| A.12.3 — Backups | No cumple | No hay backup automatizado ni probado | Implementar backup diario y restore trimestral (doc 03) |
| A.12.4 — Registro y supervision | Cumple | Logs de FastAPI, Mosquitto y Nginx disponibles | Centralizar logs |
| A.12.5 — Gestion de vulnerabilidades tecnicas | No cumple | No hay escaneo de vulnerabilidades | Implementar SAST y dependency scanning (doc 04) |
| A.12.6 — Gestion de la configuracion | Parcial | Docker Compose versionado, pero no hay hardening checklist | Crear baseline de configuracion |

### A.13 — Seguridad de las Comunicaciones

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.13.1 — Gestion de la seguridad de redes | Cumple | Nginx como proxy reverso, UFW, MQTT sobre puerto seguro | Mantener aislamiento de redes |
| A.13.2 — Intercambio de informacion | Cumple | API REST con JWT, MQTT autenticado | Documentar acuerdo de intercambio |

### A.14 — Adquisicion, Desarrollo y Mantenimiento

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.14.1 — Requisitos de seguridad en sistemas | Parcial | No hay analisis formal de requisitos de seguridad | Integrar en SDLC (doc 04) |
| A.14.2 — Seguridad en desarrollo y soporte | No cumple | No hay code review obligatorio ni SAST | Establecer CI/CD con SAST (doc 04) |

### A.16 — Gestion de Incidentes de Seguridad

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.16.1 — Gestion de incidentes | No cumple | No hay procedimiento de respuesta a incidentes | Crear plan de respuesta (doc 01) |

### A.17 — Continuidad del Negocio

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.17.1 — Continuidad de la seguridad de la informacion | No cumple | No hay BCP ni DRP | Desarrollar plan de continuidad |

### A.18 — Cumplimiento

| Control | Estado | Evidencia | Accion requerida |
|---|---|---|---|
| A.18.1 — Cumplimiento legal y contractual | No cumple | No hay revision de requisitos legales (Ley 19.628, GDPR si aplica) | Realizar auditoria legal |

---

## SOC 2 Type I — Evaluacion de Brecha

### Trust Services Criteria

| Criterio | Estado | Observaciones |
|---|---|---|
| **Security** — El sistema esta protegido contra acceso no autorizado | Parcial | Autenticacion y control de acceso existen, pero faltan monitoreo de accesos privilegiados, deteccion de intrusiones y revision de accesos |
| **Availability** — El sistema esta disponible para operacion y uso segun el compromiso | No cumple | No hay SLA definido, no hay monitoreo de uptime, no hay plan de continuidad |
| **Confidentiality** — La informacion confidencial esta protegida durante la recoleccion, uso, retencion y disposicion | No cumple | No hay clasificacion de datos, no hay cifrado en reposo, no hay politica de retencion |

### Puntos de control especificos SOC 2

| Punto de control | Estado | Evidencia |
|---|---|---|
| CC1.1 — Control environment | No cumple | No hay codigo de conducta ni politicas formalizadas |
| CC2.1 — Communication and information | Parcial | Documentacion tecnica existe, no hay comunicacion de seguridad al equipo |
| CC3.1 — Risk assessment | No cumple | No hay evaluacion formal de riesgos |
| CC4.1 — Monitoring activities | No cumple | No hay monitoreo continuo de controles |
| CC5.1 — Control activities | Parcial | Controles tecnicos implementados, faltan controles administrativos |
| CC6.1 — Logical and physical access | Parcial | Acceso logico controlado (JWT), acceso fisico: VPS con UFW |
| CC7.1 — System operations | No cumple | No hay procedimientos operacionales documentados |
| CC8.1 — Change management | Parcial | Git flow implementado, no hay proceso formal de cambios |
| CC9.1 — Risk mitigation | No cumple | No hay plan de mitigacion de riesgos |

---

## Checklist de 24 Controles — Resumen

| # | Control | ISO 27001 | SOC 2 | Estado |
|---|---|---|---|---|
| 1 | Politica de seguridad de la informacion | A.5.1 | CC1.1 | No cumple |
| 2 | Roles y responsabilidades de seguridad | A.6.1 | CC1.2 | Parcial |
| 3 | Segregacion de tareas | A.6.2 | CC2.2 | Parcial |
| 4 | Inventario de activos | A.8.1 | CC3.1 | Cumple |
| 5 | Clasificacion de la informacion | A.8.2 | CC6.1 | No cumple |
| 6 | Control de acceso (auth + roles) | A.9.1 | CC6.1 | Cumple |
| 7 | Gestion de acceso de usuarios | A.9.2 | CC6.2 | Parcial |
| 8 | Cifrado de comunicaciones (HTTPS) | A.10.1 | CC6.1 | Cumple |
| 9 | Cifrado de datos en reposo | A.10.1 | CC6.1 | No cumple |
| 10 | Gestion de claves criptograficas | A.10.2 | CC6.1 | No cumple |
| 11 | Seguridad fisica (firewall, puertos) | A.11.1 | CC6.4 | Cumple |
| 12 | Procedimientos operacionales | A.12.1 | CC7.1 | Parcial |
| 13 | Proteccion contra malware | A.12.2 | CC6.1 | Cumple |
| 14 | Backup y recuperacion | A.12.3 | CC7.1 | No cumple |
| 15 | Registro y supervision (logging) | A.12.4 | CC7.2 | Cumple |
| 16 | Gestion de vulnerabilidades tecnicas | A.12.5 | CC7.3 | No cumple |
| 17 | Seguridad en desarrollo | A.14.2 | CC8.1 | No cumple |
| 18 | Code review y SAST | A.14.2 | CC8.1 | No cumple |
| 19 | Gestion de incidentes de seguridad | A.16.1 | CC7.4 | No cumple |
| 20 | Continuidad del negocio (BCP/DRP) | A.17.1 | CC7.1 | No cumple |
| 21 | Cumplimiento legal (Ley 19.628) | A.18.1 | CC3.2 | No cumple |
| 22 | Monitoreo de accesos privilegiados | A.9.2 | CC6.1 | Parcial |
| 23 | Pruebas de restore de backups | A.12.3 | CC7.1 | No cumple |
| 24 | Dependency scanning | A.12.5 | CC8.1 | No cumple |

### Progreso general

| Estado | Cantidad | Porcentaje |
|---|---|---|
| Cumple | 9 | 37.5% |
| Parcial | 4 | 16.7% |
| No cumple | 11 | 45.8% |

---

## Matriz de Riesgos Residuales

### Criticidad de brechas

| Dominio | Controles no cumplidos | Impacto | Probabilidad | Riesgo |
|---|---|---|---|---|
| Gestion de incidentes | A.16.1, A.17.1 | Alto: sin respuesta ante incidentes, tiempo de recuperacion indefinido | Media | **Critico** |
| Cifrado y claves | A.10.1, A.10.2 | Alto: datos en reposo sin proteccion, exposicion por fuga de DB | Alta | **Critico** |
| Desarrollo seguro | A.14.2, A.12.5 | Medio-alto: vulnerabilidades en codigo sin detectar | Media | **Alto** |
| Backup | A.12.3 | Alto: perdida permanente de datos ante fallo | Baja | **Alto** |
| Acceso y usuarios | A.9.2, A.9.3 | Medio: accesos no revocados, cuentas inactivas | Media | **Medio** |
| Continuidad | A.17.1 | Alto: sin plan de recuperacion ante desastre | Baja | **Medio** |
| Cumplimiento legal | A.18.1 | Medio: incumplimiento regulatorio | Baja | **Medio** |
| Clasificacion activos | A.8.2 | Bajo: datos sin etiquetar, riesgo de mal manejo | Baja | **Bajo** |

### Plan de tratamiento

| Riesgo | Tratamiento | Prioridad | Responsable | Timeline |
|---|---|---|---|---|
| Incidentes y continuidad | Crear plan de respuesta y BCP/DRP | P0 | Director de Proyecto | Q3 2026 |
| Cifrado en reposo | Habilitar cifrado MySQL (TDE o AES) y gestion de claves | P0 | Backend/Ops | Q3 2026 |
| Desarrollo seguro | Implementar SAST (bandit/sonarqube), dependency scanning, code review obligatorio | P1 | Backend Lead | Q3 2026 |
| Backup automatizado | Configurar backup diario, probar restore trimestral | P1 | Ops | Q3 2026 |
| Acceso y usuarios | Formalizar onboarding/offboarding, revision trimestral | P2 | Director de Proyecto | Q4 2026 |
| Clasificacion de activos | Definir niveles y etiquetar activos existentes | P2 | Equipo completo | Q4 2026 |
| Cumplimiento legal | Auditoria legal externa (Ley 19.628) | P2 | Director de Proyecto | Q1 2027 |

### Matriz de riesgo residual post-remediacion

| Riesgo | Riesgo inherente | Controles propuestos | Riesgo residual | Aceptable? |
|---|---|---|---|---|
| Perdida de datos por fallo | Alto | Backup diario + restore trimestral + replicacion | Bajo | Si |
| Exposicion de datos en reposo | Critico | Cifrado AES-256 en MySQL + rotacion de claves | Bajo | Si |
| Vulnerabilidad en codigo | Alto | SAST + dependency scan + code review | Bajo | Si |
| Acceso no autorizado | Medio | JWT + roles + revision trimestral + offboarding | Bajo | Si |
| Incumplimiento regulatorio | Medio | Auditoria legal + clasificacion de datos | Bajo | Si |
| Indisponibilidad del sistema | Alto | BCP/DRP + monitoreo + SLA documentado | Medio | Si (con monitoreo continuo) |
| Incidente de seguridad sin respuesta | Critico | Plan de respuesta + equipo on-call | Medio | Parcial (depende de recursos humanos) |

---

## Proximos pasos

1. **Inmediato (Julio 2026):** Crear politicas de seguridad documentadas (docs 01-04)
2. **Corto plazo (Agosto-Septiembre 2026):** Implementar controles tecnicos prioritarios (P0)
3. **Mediano plazo (Octubre-Diciembre 2026):** Auditoria interna y remediacion de hallazgos
4. **Largo plazo (Q1-Q2 2027):** Auditoria externa ISO 27001 y SOC 2 Type I

---

> Documento generado en el contexto del proyecto academico ManttoAI — INACAP.
> Proyecto: Plataforma de Monitoreo IoT por Rubro.
