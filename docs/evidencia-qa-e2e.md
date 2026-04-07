# Evidencia de validación E2E — ManttoAI MVP

Documento de trazabilidad para la defensa académica y demo con cliente.
Completar con resultados reales al ejecutar el flujo de validación.

> Referencia: issue #44 — QA flujo end-to-end completo con hardware, alertas y predicción.

---

## Datos de la ejecución

| Campo | Valor |
|---|---|
| Fecha y hora | <!-- ej: 2026-04-07 21:00 UTC-3 --> |
| Ejecutado por | <!-- nombre del integrante --> |
| Entorno | <!-- local / VPS / demo --> |
| Versión del stack | <!-- git rev-parse --short HEAD --> |
| Origen de datos | <!-- hardware ESP32 / simulador MQTT --> |

---

## Criterio 1 — Lectura desde origen hasta dashboard

**Comando ejecutado:**
```bash
make simulate
# o: hardware ESP32 publicando a manttoai/equipo/{id}/lecturas
curl "http://localhost:8000/lecturas?equipo_id=1"
```

| Verificación | Resultado | Evidencia |
|---|---|---|
| Lectura publicada en broker MQTT | ☐ OK / ☐ FAIL | captura `mosquitto_sub` |
| Lectura persistida en backend (`/lecturas`) | ☐ OK / ☐ FAIL | salida curl / captura |
| Lectura visible en dashboard frontend | ☐ OK / ☐ FAIL | captura pantalla |

**Notas:**

---

## Criterio 2 — Alerta por condición fuera de umbral

**Comando ejecutado:**
```bash
curl -X POST "http://localhost:8000/lecturas" \
  -H "Content-Type: application/json" \
  -d '{"equipo_id":1,"temperatura":95.0,"humedad":30.0,"vib_x":2.5,"vib_y":2.5,"vib_z":25.0}'

curl "http://localhost:8000/alertas?equipo_id=1&solo_no_leidas=true&limite=100"
```

| Verificación | Resultado | Evidencia |
|---|---|---|
| Alerta generada en backend (`/alertas`) | ☐ OK / ☐ FAIL | salida curl / captura |
| Alerta visible en frontend (sección Alertas) | ☐ OK / ☐ FAIL | captura pantalla |
| Tipo de alerta correcto (temperatura / vibración) | ☐ OK / ☐ FAIL | campo `tipo` en respuesta |

**Notas:**

---

## Criterio 3 — Predicción de riesgo visible en aplicación

**Comando ejecutado:**
```bash
curl -X POST "http://localhost:8000/predicciones/ejecutar/1"
curl "http://localhost:8000/dashboard/resumen"
```

| Verificación | Resultado | Evidencia |
|---|---|---|
| Predicción ejecutada (`/predicciones/ejecutar/1` → 201) | ☐ OK / ☐ FAIL | salida curl |
| Probabilidad >= 0.5 en respuesta | ☐ OK / ☐ FAIL | campo `probabilidad` |
| Dashboard refleja `equipos_en_riesgo >= 1` | ☐ OK / ☐ FAIL | campo `equipos_en_riesgo` |
| Indicador visual de riesgo visible en frontend | ☐ OK / ☐ FAIL | captura pantalla |

**Notas:**

---

## Criterio 4 — Email de alerta SMTP (si configurado)

> Omitir si `SMTP_HOST` no está configurado en `backend/.env`.

**Comando ejecutado:**
```bash
python scripts/test_smtp_real.py
# o automáticamente via: bash scripts/smoke_test.sh
```

| Verificación | Resultado | Evidencia |
|---|---|---|
| Script `test_smtp_real.py` finaliza con SUCCESS | ☐ OK / ☐ OMITIDO / ☐ FAIL | salida terminal |
| Email recibido en bandeja de destino | ☐ OK / ☐ OMITIDO / ☐ FAIL | captura email |
| Asunto y cuerpo contienen datos útiles de alerta | ☐ OK / ☐ OMITIDO / ☐ FAIL | captura email |

**Notas:**

---

## Criterio 5 — Smoke test automatizado completo

**Comando ejecutado:**
```bash
bash scripts/smoke_test.sh
```

| Verificación | Resultado | Evidencia |
|---|---|---|
| Script finaliza con `Smoke test completado correctamente ✅` | ☐ OK / ☐ FAIL | salida terminal |
| Escenario 1 (lecturas) en verde | ☐ OK / ☐ FAIL | log smoke |
| Escenario 2 (alertas) en verde | ☐ OK / ☐ FAIL | log smoke |
| Escenario 3 (predicción + dashboard) en verde | ☐ OK / ☐ FAIL | log smoke |
| Escenario 4 SMTP (si aplica) en verde | ☐ OK / ☐ OMITIDO | log smoke |

**Salida completa del smoke (pegar aquí o adjuntar como archivo):**
```
<!-- pegar salida de bash scripts/smoke_test.sh -->
```

---

## Resumen de validación

| Criterio | Estado |
|---|---|
| Lectura origen → dashboard | ☐ PASS / ☐ FAIL |
| Alerta por umbral visible | ☐ PASS / ☐ FAIL |
| Predicción de riesgo en app | ☐ PASS / ☐ FAIL |
| Email SMTP (si aplica) | ☐ PASS / ☐ OMITIDO / ☐ FAIL |
| Smoke test automatizado | ☐ PASS / ☐ FAIL |

**Veredicto final:** ☐ MVP validado — listo para demo/defensa &nbsp;&nbsp; ☐ Pendiente resolución de issues

**Firmado por:** <!-- nombre(s) del equipo -->

---

## Archivos de evidencia adjuntos

<!-- Listar capturas, videos o logs guardados para el informe -->
- `evidencia/smoke-YYYYMMDD-HHMM.txt`
- `evidencia/captura-dashboard-YYYYMMDD.png`
- `evidencia/captura-alertas-YYYYMMDD.png`
- `evidencia/captura-email-YYYYMMDD.png` (si aplica)
