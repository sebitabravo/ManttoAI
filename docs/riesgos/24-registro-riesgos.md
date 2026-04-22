# 24. Registro de Riesgos

| ID | Riesgo | Categoría | Prob. | Impacto | Puntaje | Plan de Respuesta | Resp. | Estado |
|----|--------|-----------|-------|---------|---------|-------------------|-------|--------|
| R01 | Inestabilidad Wi-Fi en ESP32 | Técnico | Alta | Alto | 9 | Implementar simulador MQTT backend 24/7 | Sebastián | ✅ Mitigado |
| R02 | Modelo ML con Accuracy < 80% | Técnico | Media | Alto | 6 | Tuning de hiperparámetros y dataset sintético | Ángel | ✅ Cerrado (F1=94%) |
| R03 | Retraso importación sensores | Logístico | Media | Medio | 4 | Comprar stock local (MercadoLibre) | Sebastián | ✅ Cerrado |
| R04 | Frontend desactualizado (Stale Data) | Técnico | Baja | Alto | 3 | Implementar auto-refresh/polling en React | Luis | ✅ Mitigado |
| R05 | Caída VPS durante Demo | Infra | Baja | Alto | 3 | Script local de Docker Compose de respaldo | Sebastián | Activo |
| R06 | Falla de Integración Continua (CI) | Calidad | Media | Medio | 4 | Uso de tests automatizados y linting estricto | Sebastián | Activo |
| R07 | Sobrepaso de presupuesto | Gestión | Baja | Medio | 2 | Uso exclusivo de Open-Source y VPS económico | Sebastián | ✅ Cerrado |
