# ADR-003: Sistema de alertas por email como canal de notificaciones

**Fecha:** 2024-11-25  
**Estado:** Aceptado  
**Contexto:** Necesitamos un mecanismo para notificar a los usuarios cuando se detectan anomalías o alertas críticas. Las opciones consideradas fueron: Email, SMS, push notifications (Firebase), y WebSocket en tiempo real.

**Decisión:** Usar email como canal primario de notificaciones, con opción de marcar alertas como "leídas" en la UI.

**Razones:**
1. **Simplicidad**: SMTP es fácil de integrar con Python (smtplib), no requiere servicios externos como Twilio o Firebase.
2. **Sin costo**: Usando Gmail SMTP o servicios similares, no hay costo adicional para el MVP académico.
3. **Trazabilidad**: Los emails quedan registrados en bandeja de entrada, útil para auditoría en el informe.
4. **No bloqueante**: Si el email falla, la alerta se crea igualmente en la base de datos y se puede ver en el dashboard.
5. **Scope académico**: El proyecto no requiere notificaciones en tiempo real push.

**Consecuencias:**
- Positives: Easy integration, no dependencies, works offline.
- Negatives: No real-time, depends on SMTP server availability.

**Notas:** Para producción se debería considerar un servicio transactional email (SendGrid, Mailgun). Para el MVP académico con Gmail o servicio SMTP del ISP es suficiente.