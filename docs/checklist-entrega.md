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
- [ ] Endpoint `/alertas` devuelve al menos una alerta activa tras escenario de breach
- [ ] Endpoint `/predicciones/ejecutar/{equipo_id}` responde `201`
- [ ] Endpoint `/dashboard/resumen` refleja probabilidad y equipos en riesgo
- [ ] Frontend muestra Dashboard, Equipos, Alertas e Historial sin errores de carga

## C. Smoke pre-demo

- [ ] `bash scripts/smoke_test.sh` finaliza con `Smoke test completado correctamente`
- [ ] Si falla, se resolvió causa raíz y se repitió smoke exitoso

## D. Evidencia para entrega

- [ ] Capturas o video del flujo completo (normal + alerta + riesgo)
- [ ] Enlaces de PR y commits relevantes listos para anexar en informe
- [ ] README y docs (`docs/demo.md`, `docs/manual-usuario.md`) actualizados

## E. Plan de contingencia para defensa

- [ ] Preparado comando de recuperación rápida: `make down && make up`
- [ ] Preparado plan B para modelo ausente: `docker compose exec backend python /app/app/ml/train.py`
- [ ] Datos demo resembrables con `make seed`

## F. Cierre académico

- [ ] Alcance de MVP validado (sin sobreprometer features fuera de scope)
- [ ] Mensaje final de demo alineado a PMBOK (objetivo, evidencia, resultado)
