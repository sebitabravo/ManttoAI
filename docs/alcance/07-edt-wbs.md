# 07. Estructura de Desglose del Trabajo (EDT/WBS)

## EDT Jerárquica

1. **ManttoAI — Plataforma de Monitoreo IoT por Rubro**
   1.1 Gestión del Proyecto
       1.1.1 Planificación PMBOK
       1.1.2 Control y Seguimiento (Sprints)
       1.1.3 Cierre y Defensa
   1.2 Módulo IoT
       1.2.1 Hardware (ESP32, DHT22, MPU-6050)
       1.2.2 Simulador IoT 24/7 (Software)
       1.2.3 Comunicación MQTT (Mosquitto)
   1.3 Backend
       1.3.1 API FastAPI
       1.3.2 Base de datos MySQL
       1.3.3 Servicios (auth, alertas, mqtt)
   1.4 Modelo de IA
       1.4.1 Dataset de entrenamiento (sintético/C-MAPSS)
       1.4.2 Modelo Random Forest
       1.4.3 Integración con backend API
   1.5 Frontend
       1.5.1 Dashboard React / Vite
       1.5.2 Integración Auto-refresh
   1.6 Infraestructura
       1.6.1 Docker y Docker Compose
       1.6.2 Deploy VPS (Dokploy)
       1.6.3 CI/CD GitHub Actions
   1.7 Calidad
       1.7.1 Pruebas Unitarias Backend (Pytest)
       1.7.2 Pruebas E2E Frontend (Playwright)

## Diccionario WBS Resumido

| Código | Entregable | Responsable | Estado Implementación |
|--------|------------|-------------|-----------------------|
| 1.2.2 | Simulador IoT | Sebastián B. | ✅ Implementado |
| 1.3.1 | API FastAPI | Sebastián B. | ✅ Implementado |
| 1.4.2 | Modelo Random Forest | Ángel R. | ✅ Implementado (Acc 94.1%, F1 93.0%) |
| 1.5.1 | Dashboard React | Luis L. | ✅ Implementado |
| 1.6.3 | CI/CD Actions | Sebastián B. | ✅ Implementado |
| 1.7.2 | Pruebas E2E | Equipo QA | ✅ Implementado (7 flujos) |
