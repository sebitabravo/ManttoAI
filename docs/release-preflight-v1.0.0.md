# Release Preflight v1.0.0

Checklist de verificación final antes del code freeze.

**Fecha de verificación:** 2026-04-07  
**Issue relacionada:** #59  
**PR:** #82

---

## Criterios de aceptación (Issue #59)

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| No quedan residuos obvios de debug innecesario | ✅ | `rg 'console\.log' frontend/src` → sin resultados; `rg 'breakpoint\|pdb\.set_trace' backend/` → sin resultados |
| `.env`, secretos y artefactos sensibles fuera de git | ✅ | `git ls-files \| rg '\.env$\|\.pem$\|\.key$\|modelo\.joblib'` → sin coincidencias |
| Verificación final ejecutada | ✅ | Ver sección "Comandos ejecutados" |
| Repo listo para congelar versión final | ✅ | Todos los checks pasan, `.gitignore` actualizado |

---

## Comandos ejecutados

### Docker Compose

```bash
$ docker compose config --quiet
✅ docker compose config: válido
```

### Frontend Build

```bash
$ npm run build
vite v6.4.1 building for production...
✓ 132 modules transformed.
dist/index.html                   0.93 kB │ gzip:  0.58 kB
dist/assets/index-Beg-C6XE.css    7.73 kB │ gzip:  2.51 kB
dist/assets/index-F_k2Rm95.js   258.38 kB │ gzip: 82.57 kB
✓ built in 629ms
```

### Backend Tests

```bash
$ pytest tests/ -q --tb=no
105 passed, 2 skipped in 16.05s
```

### Verificación de secretos

```bash
$ git ls-files | rg -i '\.env$|\.pem$|\.key$|modelo\.joblib|mosquitto/passwd'
✅ No hay archivos sensibles trackeados
```

### Verificación de código debug

```bash
$ rg 'console\.log' frontend/src/
# Sin resultados

$ rg 'breakpoint\(\)|pdb\.set_trace|ipdb' backend/
# Sin resultados

$ rg 'debugger' frontend/src/
# Sin resultados
```

---

## Archivos modificados en este release

| Archivo | Cambio |
|---------|--------|
| `.gitignore` | Agregados patrones para ignorar artefactos temporales de QA |
| `backend/app/ml/train.py` | Reemplazado `print()` por `logging` en bloque `__main__` |
| `backend/app/ml/evaluate.py` | Reemplazado `print()` por `logging` en bloque `__main__` |
| `backend/app/ml/generate_dataset.py` | Reemplazado `print()` por `logging` en bloque `__main__` |
| `docs/release-preflight-v1.0.0.md` | Documento de evidencia de verificación (este archivo) |

---

## Patrones agregados al .gitignore

```gitignore
# === QA / Testing temporal ===
qa-*.png
audit-*.png
.playwright-mcp/
pr_review_comment.md
```

---

## Verificación funcional de la demo (Playwright)

Verificación visual completa realizada el 2026-04-07 con Playwright MCP.

### Dashboard Principal
- ✅ 3 equipos registrados
- ✅ 5 alertas activas mostradas
- ✅ 2 equipos en estado de riesgo
- ✅ Predicción de falla máxima: 96.1%

### Gestión de Equipos
- ✅ Lista de equipos con clasificación de riesgo (Normal/Alerta/Falla)
- ✅ Probabilidades ML visibles por equipo
- ✅ Detalle individual con predicción, umbrales editables, lecturas, mantenciones

### Predicción ML en vivo
| Equipo | Probabilidad | Clasificación |
|--------|--------------|---------------|
| Compresor Línea A | 62.5% | ⚠️ Alerta |
| Bomba Hidráulica B | 25.6% | ✅ Normal |
| Motor Ventilación C | 96.1% → 72.2% | 🔴 Falla → ⚠️ Alerta |

### Flujo MQTT → Backend → ML → Frontend
Test en vivo ejecutado:

```bash
# Publicación MQTT con credenciales
docker exec manttoai-mosquitto-1 mosquitto_pub \
  -h localhost -u manttoai_mqtt -P manttoai_mqtt_dev \
  -t "manttoai/equipo/3/lecturas" \
  -m '{"temperatura":85.5,"humedad":78.2,"vib_x":8.5,"vib_y":7.2,"vib_z":9.1}'
```

**Resultado:**
- ✅ Lectura apareció en frontend (85.50°C, 78.20%, 9.10g)
- ✅ Modelo ML se re-ejecutó automáticamente
- ✅ Predicción cambió de 96.1% (Falla) a 72.2% (Alerta)
- ✅ Timestamp correcto: 07-04-2026, 05:30 a.m.

### Screenshots de evidencia
- `qa-equipo-detalle-prediccion-ml.png` - Detalle de equipo con predicción ML
- `qa-mqtt-live-test-prediction-updated.png` - Flujo MQTT en vivo

---

## Pasos para crear el tag v1.0.0

Una vez mergeado el PR #82:

```bash
# 1. Actualizar main
git checkout main
git pull origin main

# 2. Crear tag anotado
git tag -a v1.0.0 -m "ManttoAI v1.0.0 - MVP funcional para demo académica

Incluye:
- Backend FastAPI con auth JWT, CRUD completo, alertas y predicciones
- Frontend React con dashboard, gestión de equipos y visualizaciones
- Pipeline ML con Random Forest (accuracy >= 80%)
- Integración MQTT para telemetría IoT
- Docker Compose para despliegue local y producción

Cierre técnico: Issue #59"

# 3. Push del tag
git push origin v1.0.0
```

---

## Verificación post-merge

Después de crear el tag, verificar en GitHub:

- [ ] Release v1.0.0 visible en la página de releases
- [ ] Issue #59 cerrada automáticamente
- [ ] PR #82 mergeado correctamente

---

**Verificado por:** CI/CD + revisión manual  
**Estado:** ✅ Listo para code freeze
