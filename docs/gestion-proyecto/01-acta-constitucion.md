# 01. Acta de Constitución del Proyecto (Project Charter)

**Nombre del Proyecto:** ManttoAI — Plataforma de Monitoreo IoT por Rubro  
**Fecha de Inicio:** Semana 1 (Febrero 2026)  
**Fecha de Fin:** Semana 24 (Julio 2026)  
**Patrocinador:** Director de Carrera INACAP  
**Director del Proyecto:** Sebastián Bravo  

## Propósito y Justificación
Desarrollar una plataforma de monitoreo IoT por rubro (industrial, agrícola, comercial) que permita a empresas medianas monitorear el estado de sus equipos mediante IoT y Machine Learning, evitando paradas no planificadas. Académicamente, el proyecto valida las competencias en Gestión de Proyectos Informáticos y Desarrollo Full-Stack.

## Objetivos
- **Objetivo General:** Capturar telemetría IoT y predecir fallas mediante un modelo ML en un dashboard web.
- **Objetivos Específicos:**
  1. Capturar lecturas (temp, humedad, vibración) desde ESP32 vía MQTT.
  2. Implementar modelo Random Forest para evaluación de riesgos.
  3. Desplegar sistema en VPS con alertas en tiempo real.

## Criterios de Éxito
- **Calidad ML:** Accuracy ≥ 80% (Logrado: 94.1%) y F1-Score ≥ 80% (Logrado: 93.0%)
- **Calidad Código:** Cobertura de tests ≥ 70% (Logrado: 82%)
- **Rendimiento:** Tiempos de respuesta API < 500ms
- **Completitud:** Repositorio en GitHub con CI/CD automatizado.

## Premisas y Restricciones
- **Restricciones:** Uso exclusivo de herramientas open-source y scikit-learn. Equipo de 3 personas. Presupuesto limitado. No se integrará con ERPs corporativos reales.
- **Premisas:** Conectividad Wi-Fi disponible para los ESP32.

## Presupuesto Resumido
- **Prototipo académico:** Costo real USD $98 (3 kits ESP32 + VPS Hetzner). Presupuesto simulado CLP $9.790.000.
- **Plan de negocios (Evaluación 3 — Gestión de Costos):** Capital inicial $3.000.000 CLP (3 socios). Costos operacionales $187.100 CLP/mes. Detalle completo en [`docs/costos/12-plan-gestion-costos.md`](../costos/12-plan-gestion-costos.md).

## Nivel de Autoridad
El Director de Proyecto tiene autoridad para asignar tareas, aprobar pull requests y decidir la arquitectura base, siempre respetando las restricciones presupuestarias y de alcance.
