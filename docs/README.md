# 📚 Documentación de ManttoAI — Plataforma de Monitoreo IoT por Rubro

Bienvenido al directorio central de documentación de **ManttoAI**. Este espacio está diseñado para servir tanto a desarrolladores de la comunidad Open Source que deseen contribuir o entender la plataforma, como a evaluadores académicos que requieran revisar los artefactos formales de gestión del proyecto (PMBOK).

---

## 🛠️ 1. Documentación Técnica (Core)
Guías fundamentales para entender cómo funciona el sistema por debajo y cómo operarlo.

* **[Arquitectura del Sistema](arquitectura-manttoai.md)**: Visión global de los componentes (ESP32, Mosquitto, FastAPI, React).
* **[API Endpoints](api-endpoints.md)**: Documentación de los endpoints REST del backend.
* **[Modelo Machine Learning](modelo-ml.md)**: Explicación del modelo predictivo (Random Forest) y sus métricas.
* **[Guía de Despliegue (Dokploy)](despliegue-dokploy.md)**: Cómo llevar la plataforma a producción en un VPS.
* **[Gestión de Secretos](deploy-secrets.md)**: Manejo seguro de credenciales en entornos productivos.
* **[Backup y Restauración](backup-restauracion.md)**: Políticas de respaldo para la base de datos y configuraciones.

## 👥 2. Guías de Usuario y Operación
* **[Manual de Usuario](manual-usuario.md)**: Guía de uso del dashboard web interactivo.
* **[Guía de Demo](demo.md)**: Cómo ejecutar la demostración completa con el simulador IoT.

## 🤖 3. Desarrollo Asistido por IA (Flujos de Trabajo)
ManttoAI fue construido utilizando prácticas modernas de desarrollo colaborativo con IA. Aquí documentamos nuestros estándares:
* **[Flujo de Trabajo con IA](flujo-trabajo-ia.md)**: Reglas y convenciones del equipo para interactuar con agentes.
* **[Plantilla de Code Review IA](plantilla-code-review-ia.md)**: Prompt y rúbrica para auditorías de código automatizadas.

## 🏛️ 4. Decisiones de Arquitectura (ADRs)
Registro histórico de por qué se tomaron ciertas decisiones tecnológicas clave.
* **[ADR-001: Comunicación MQTT](decisiones/ADR-001-comunicacion-mqtt.md)**
* **[ADR-002: Modelo ML Random Forest](decisiones/ADR-002-modelo-ml-random-forest.md)**
* **[ADR-003: Alertas por Email](decisiones/ADR-003-alertas-email.md)**

---

## 🎓 5. Gestión del Proyecto (PMBOK 6ª Edición - INACAP)

*Documentación formal requerida para la evaluación de la asignatura de Gestión de Proyectos Informáticos.*

**[📄 Informe PMBOK Final (Resumen Ejecutivo Académico)](informe-pmbok-final.md)**

### Integración
* [00. Resumen Ejecutivo (Gestión)](gestion-proyecto/00-resumen-ejecutivo.md)
* [01. Acta de Constitución (Charter)](gestion-proyecto/01-acta-constitucion.md)
* [02. Plan de Dirección de Proyecto](gestion-proyecto/02-plan-direccion-proyecto.md)
* [03. Registro de Lecciones Aprendidas](gestion-proyecto/03-registro-lecciones-aprendidas.md)
* [04. Acta de Cierre](gestion-proyecto/04-acta-cierre.md)

### Alcance
* [05. Plan de Gestión del Alcance](alcance/05-plan-gestion-alcance.md)
* [06. Enunciado del Alcance](alcance/06-enunciado-alcance.md)
* [07. EDT / WBS (Estructura de Desglose)](alcance/07-edt-wbs.md)
* [08. Matriz de Trazabilidad de Requisitos](alcance/08-matriz-trazabilidad-requisitos.md)

### Cronograma y Costos
* [09. Plan de Gestión del Cronograma](cronograma/09-plan-gestion-cronograma.md)
* [10. Lista de Actividades](cronograma/10-lista-actividades.md)
* [11. Hitos del Proyecto](cronograma/11-hitos-proyecto.md)
* [12. Plan de Gestión de Costos](costos/12-plan-gestion-costos.md)
* [13. Estimación de Costos Detallada](costos/13-estimacion-costos-detallada.md)
* [14. Línea Base de Costos](costos/14-linea-base-costos.md)

### Calidad y Recursos
* [15. Plan de Gestión de Calidad](calidad/15-plan-gestion-calidad.md)
* [16. Métricas de Calidad](calidad/16-metricas-calidad.md)
* [17. Reporte Final de Control de Calidad](calidad/17-reporte-control-calidad.md)
* [18. Organigrama del Proyecto](recursos/18-organigrama-proyecto.md)
* [19. Matriz RACI](recursos/19-matriz-raci.md)
* [20. Plan de Capacitación del Equipo](recursos/20-plan-capacitacion-equipo.md)

### Riesgos, Comunicaciones e Interesados
* [21. Plan de Comunicaciones](comunicaciones/21-plan-gestion-comunicaciones.md)
* [22. Matriz de Comunicaciones](comunicaciones/22-matriz-comunicaciones.md)
* [23. Plan de Gestión de Riesgos](riesgos/23-plan-gestion-riesgos.md)
* [24. Registro de Riesgos](riesgos/24-registro-riesgos.md)
* [25. Matriz de Probabilidad e Impacto](riesgos/25-matriz-probabilidad-impacto.md)
* [26. Plan de Adquisiciones](adquisiciones/26-plan-gestion-adquisiciones.md)
* [27. Registro de Interesados](interesados/27-registro-interesados.md)
* [28. Matriz Poder/Interés](interesados/28-matriz-poder-interes.md)
* [29. Plan de Involucramiento](interesados/29-plan-involucramiento-interesados.md)

---
*Mantenido por el equipo de ManttoAI. La documentación técnica se actualiza junto con el código fuente.*
