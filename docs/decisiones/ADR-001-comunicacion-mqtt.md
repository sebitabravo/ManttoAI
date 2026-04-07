# ADR-001: Arquitectura de comunicación IoT via MQTT

**Fecha:** 2024-11-15  
**Estado:** Aceptado  
**Contexto:** Necesitamos un mecanismo de comunicación entre los dispositivos ESP32 y el backend. Las opciones consideradas fueron: HTTP REST directo, WebSocket, MQTT, y protocolo propietario.

**Decisión:** Usar MQTT como protocolo de comunicación entre los ESP32 y el backend.

**Razones:**
1. **Ligero**: MQTT tiene overhead mínimo comparado con HTTP, ideal para dispositivos con recursos limitados.
2. **Bidireccional**: Permite publicación y suscripción, facilitando alertas push hacia los dispositivos si se necesita en el futuro.
3. **Reconexión automática**: La librería PubSubClient maneja reconexiones automáticamente.
4. **Escalable**: Broker Mosquitto puede manejar miles de dispositivos simultáneos.
5. **Separación de responsabilidades**: El broker actúa como buffer, el backend no necesita exponer endpoints públicos para IoT.

**Consecuencias:**
- Positivas: Menor consumo de batería en ESP32, arquitectura desacoplada, fácil monitoreo del broker.
- Negativas: Agrega complejidad en infraestructura (Mosquitto), requiere autenticación configurada.

**Notas:** Para el MVP académico, MQTT sobre WiFi es suficiente. No se considera LoRa, 4G, Modbus u OPC-UA por las restricciones del proyecto (ver AGENTS.md).