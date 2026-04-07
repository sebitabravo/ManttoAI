# Checklist final de demo y entrega

Usar esta lista antes de grabar video o presentar defensa.

## A. Entorno técnico

- [ ] `make setup-env` ejecutado sin errores
- [ ] `make config` en verde
- [ ] `make up` con contenedores `backend`, `frontend`, `mysql`, `mosquitto`, `nginx` activos
- [ ] `curl http://localhost:8000/health` responde `200`

## B. Flujo funcional MVP

- [ ] `make seed` ejecutado y con equipos/umbrales cargados
- [ ] `make simulate` ejecutado y con lecturas persistidas
- [ ] `make verify-3-nodes` en verde para equipos `1`, `2`, `3`
- [ ] Endpoint `/alertas` devuelve al menos una alerta activa tras escenario de breach
- [ ] Endpoint `/predicciones/ejecutar/{equipo_id}` responde `201`
- [ ] Endpoint `/dashboard/resumen` refleja probabilidad y equipos en riesgo
- [ ] Frontend muestra Dashboard, Equipos, Alertas e Historial sin errores de carga

## C. Criterios de aceptación E2E (issue #44)

- [ ] Una lectura llega desde el origen final (hardware o simulador) hasta el dashboard
- [ ] Una condición fuera de umbral genera alerta visible en frontend
- [ ] Una predicción relevante (probabilidad >= 0.5) se refleja en la aplicación
- [ ] Si SMTP está configurado: email de alerta llega con datos útiles (`python scripts/test_smtp_real.py`)
- [ ] Queda evidencia suficiente para defensa o demo (ver sección D)

## D. Smoke pre-demo

- [ ] `bash scripts/smoke_test.sh` finaliza con `Smoke test completado correctamente`
- [ ] Escenario SMTP: si `SMTP_HOST` está configurado, el smoke lo valida automáticamente
- [ ] Si falla, se resolvió causa raíz y se repitió smoke exitoso

## E. Evidencia para entrega

- [ ] Capturas o video del flujo completo (normal + alerta + riesgo)
- [ ] Captura de `mosquitto_sub` mostrando topics de 3 equipos (`1`, `2`, `3`)
- [ ] Captura de dashboard con 3 equipos activos en simultáneo
- [ ] Salida de `bash scripts/smoke_test.sh` guardada como evidencia
- [ ] Si SMTP activo: captura del email recibido con datos de alerta
- [ ] Enlaces de PR y commits relevantes listos para anexar en informe
- [ ] README y docs (`docs/demo.md`, `docs/manual-usuario.md`) actualizados

## F. Plan de contingencia para defensa

- [ ] Preparado comando de recuperación rápida: `make down && make up`
- [ ] Preparado plan B para modelo ausente: `docker compose exec backend python /app/app/ml/train.py`
- [ ] Datos demo resembrables con `make seed`

## G. Cierre académico

- [ ] Alcance de MVP validado (sin sobreprometer features fuera de scope)
- [ ] Mensaje final de demo alineado a PMBOK (objetivo, evidencia, resultado)
- [ ] `docs/evidencia-qa-e2e.md` completado con resultados reales de la validación
