# 01. Acta de Constitución del Proyecto (Project Charter)

**Nombre del Proyecto:** ManttoAI Predictivo  
**Fecha de Inicio:** Semana 1 (Febrero 2026)  
**Fecha de Fin:** Semana 24 (Julio 2026)  
**Patrocinador:** Director de Carrera INACAP  
**Director del Proyecto:** Sebastián Bravo  

## Propósito y Justificación
Desarrollar un prototipo de mantenimiento predictivo de bajo costo que permita a industrias medianas monitorear el estado de sus equipos mediante IoT y Machine Learning, evitando paradas no planificadas. Académicamente, el proyecto valida las competencias en Gestión de Proyectos Informáticos y Desarrollo Full-Stack.

## Objetivos
- **Objetivo General:** Capturar telemetría IoT y predecir fallas mediante un modelo ML en un dashboard web.
- **Objetivos Específicos:**
  1. Capturar lecturas (temp, humedad, vibración) desde ESP32 vía MQTT.
  2. Implementar modelo Random Forest para evaluación de riesgos.
  3. Desplegar sistema en VPS con alertas en tiempo real.

## Criterios de Éxito
- **Calidad ML:** F1-Score ≥ 85% (Logrado: 94.1%)
- **Calidad Código:** Cobertura de tests ≥ 70% (Logrado: 82%)
- **Rendimiento:** Tiempos de respuesta API < 500ms
- **Completitud:** Repositorio en GitHub con CI/CD automatizado.

## Premisas y Restricciones
- **Restricciones:** Uso exclusivo de herramientas open-source y scikit-learn. Equipo máximo de 4 personas. Presupuesto limitado. No se integrará con ERPs corporativos reales.
- **Premisas:** Conectividad Wi-Fi disponible para los ESP32.

## Presupuesto Resumido
El presupuesto académico simulado asciende a **CLP $9.790.000**, que incluye costos de infraestructura AWS, sensores y honorarios del equipo durante 6 meses. (Costo real de MVP: USD $98).

## Nivel de Autoridad
El Director de Proyecto tiene autoridad para asignar tareas, aprobar pull requests y decidir la arquitectura base, siempre respetando las restricciones presupuestarias y de alcance.
