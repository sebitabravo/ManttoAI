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
