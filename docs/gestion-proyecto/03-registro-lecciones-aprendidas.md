# 03. Registro de Lecciones Aprendidas

| ID | Categoría | Lección Aprendida (Basada en el Repositorio) | Recomendación Futura |
|----|-----------|----------------------------------------------|----------------------|
| L01 | Técnico/ML | **Random Forest superó expectativas:** Un modelo clásico (scikit-learn) logró 94.1% de F1-Score con bajo consumo de CPU. | Evitar Deep Learning para MVPs predictivos si los datos tubulares son suficientes. |
| L02 | Testing | **Testing tardío genera deuda técnica:** Los tests automatizados (Pytest) se desarrollaron cerca del code freeze, causando refactorización de fixtures de base de datos. | Iniciar TDD o escribir tests en paralelo con la implementación de los endpoints. |
| L03 | DevOps | **Dokploy simplifica el GitOps:** Migrar de Docker Compose manual a Dokploy permitió despliegues automáticos al hacer merge en `main`. | Estandarizar Dokploy (o similar) desde el inicio del proyecto. |
| L04 | UX/Frontend| **Frontend reactivo requiere auto-refresh:** El dashboard no era útil sin polling de datos. Se tuvo que re-escribir lógica con `usePolling` en React. | Definir requisitos de tiempo real (WebSockets vs Polling) en la fase de diseño de arquitectura. |
| L05 | IoT | **Dependencia de hardware bloquea el desarrollo:** Integrar un Simulador MQTT 24/7 en el backend destrabó el desarrollo del dashboard sin depender del ESP32 físico. | Siempre construir un simulador de software para componentes de hardware en proyectos IoT. |
