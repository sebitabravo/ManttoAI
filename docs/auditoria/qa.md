# Auditoría QA — Verificación de suite de tests (2026-08-16)

> **Nota de vigencia:** los conteos siguientes son evidencia histórica de la auditoría.
> Deben contrastarse con la salida fresca de los comandos de verificación y con
> [`estado-implementacion.md`](estado-implementacion.md) antes de presentarlos como estado
> actual.

## Addendum de estado actual

La verificación posterior a esta línea base ejecutó el runner raíz `./test.sh`
con **370 passed y 3 skipped** (373 tests recolectados), `make test` con **86 %
de cobertura**, frontend con **59 tests unitarios**, lint/build sin errores y
Playwright **22/22**. `npm audit --omit=dev --audit-level=moderate` no reporta
vulnerabilidades moderadas o superiores. Los únicos skips siguen siendo gates
opt-in de SMTP real, concurrencia MySQL y roundtrip MySQL de Alembic; no deben
confundirse con fallos de la suite. El estado consolidado y los pendientes
externos están en [`estado-implementacion.md`](estado-implementacion.md).

## Resumen ejecutivo

**Backend: verde. Frontend: verde. Suite completa NO es 100% verde por un blocker de entorno (MySQL no disponible), no por fallos de test.**

| Área | Resultado | Evidencia |
|---|---|---|
| Backend pytest (unit + integración SQLite) | **317 passed, 3 skipped, 0 failed** | `pytest.ini` + salida completa abajo |
| Cobertura backend | **85.15%** (piso configurado: 80%) | `--cov-fail-under=80` pasó |
| Backend ruff | **0 issues** | "All checks passed!" |
| Backend black --check | **0 issues** | "83 files would be left unchanged" |
| Frontend ESLint (`--max-warnings=0`) | **0 issues** | sin output = sin warnings/errors |
| Frontend Vitest | **53 passed / 53** (10 archivos) | ver salida abajo |
| Frontend build (vite build) | **OK**, 1860 módulos, sin errores | ver salida abajo |
| Frontend Playwright E2E | **22 passed / 22** (11 specs × chromium + firefox) | ver salida abajo |
| Tests de integración MySQL real | **BLOQUEADO** — no hay contenedor `mysql` de ManttoAI corriendo | `docker compose ps mysql` → vacío |

Reconciliación del conteo "317 tests": el commit `9e3b835` (10-jun-2026) ya declaraba textualmente
`317 passed, 3 skipped, 0 failed` en su mensaje. La corrida de hoy reproduce ese número exacto,
dos meses después, sin tocar el código de tests. El número "242" reportado en una pasada anterior
no es reproducible con ningún método de conteo razonable (grep recursivo con cualquier patrón de
indentación da 313 funciones `def test_` crudas; pytest expande a 320 nodos por 3 `parametrize`;
317 pasan + 3 se saltan = 320). La hipótesis más probable es que ese conteo de 242 se ejecutó desde
un directorio equivocado o con un comando que no recorrió `tests/` completo — no hay evidencia de
que el repo haya tenido alguna vez sólo 242 tests desde el 10-jun.

## Ambiente

El venv de `backend/.venv` estaba **roto** al iniciar la verificación: symlink colgante a un
intérprete `cpython-3.13` que `uv` ya no tiene instalado localmente (solo quedan 3.11 y 3.12
en `~/.local/share/uv/python/`). Se recreó con `uv venv --python 3.11 .venv` (ignorado por
`.gitignore:19`, cambio puramente local, no versionado) y se reinstalaron las dependencias con
`uv pip install -r requirements.txt -r requirements-dev.txt`. Sin este paso, ningún comando pedido
podía ejecutarse.

Frontend: `node_modules/` ya existía; se ejecutó `npm ci` igualmente para garantizar reproducibilidad
desde el lockfile (331 paquetes instalados, 0 errores de instalación).

---

## 1. Backend — pytest + cobertura

Comando: `pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80`

```
======================= 317 passed, 3 skipped in 57.32s ========================

Required test coverage of 80% reached. Total coverage: 85.15%
```

Cobertura por módulo — los archivos por debajo del promedio general (85.15%), útiles para priorizar:

```
Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
app/routers/metrics.py                           152     78    49%   42, 58-63, 101-119, 135-139, 150-158, 164, 178-207, 230-270, 284-311
app/utils/logging_config.py                       28     11    61%   15-16, 45-58, 68-79, 91-102
app/middleware/rate_limit.py                      72     25    65%   35, 79, 91-94, 112, 120-126, 148-183
app/services/lectura_service.py                   77     27    65%   80-130, 139
app/dependencies.py                              124     39    69%   30-34, 43, 90, 109-116, 121, 128-129, 138-139, 147-148, 203-242
app/services/prediccion_service.py               169     52    69%   50, 55, 76-77, 81-83, 108-136, 153, 160, 172, 185, 197-203, 218, 259-301
app/middleware/tenant.py                          22      6    73%   39-47
app/main.py                                      135     36    73%   59-74, 84, 87, 90, 93, 99, 102, 105, 254-255, 260-267, 273-284
app/services/email_service.py                    100     26    74%   32, 41, 45, 68-80, 95-96, 126, 134-162
app/services/mqtt_service.py                     151     39    74%   47-49, 55-57, 73, 86, 89-90, 93, 130-133, 178-180, 212-222, 228-231, 237-241, 250-251, 254, 265, 279-287
app/routers/audit_logs.py                         19      5    74%   56-64
app/services/alerta_service.py                   169     39    77%   44, 47-50, 58, 68, 83, 87, 215-217, 232, 236, 252, 264-273, 285-288, 304-305, 328, 331, 350-356, 394-410
app/services/prediccion_scheduler_service.py     137     30    78%   37, 49-51, 61, 65, 88, 100-106, 163-167, 181-185, 195-199, 204-206, 214-215, 222, 237-245
----------------------------------------------------------------------------
TOTAL                                           3703    550    85%
```

### Los 3 skipped (detalle, no truncado)

```
SKIPPED [1] tests/integration/test_smtp_integration.py:16: Configuración SMTP incompleta en .env para test de integración
SKIPPED [1] tests/test_concurrency_alerts.py:28: La prueba de concurrencia requiere MySQL real y habilitación explícita
SKIPPED [1] tests/test_rate_limit_by_role.py:61: Rate limiting diferenciado por rol no implementado aún en dashboard router
```

El tercero no es un blocker de entorno: es un `@pytest.mark.skip` permanente porque la
funcionalidad que prueba (rate limiting diferenciado por rol en `/dashboard/resumen`) **no está
implementada**. El test existe pero documenta deuda de producto, no un problema de esta corrida.

### Tests de integración marcados `@pytest.mark.integration`

```
pytest tests/ -v -m "integration"
collected 320 items / 319 deselected / 1 selected
tests/integration/test_smtp_integration.py::test_real_smtp_integration SKIPPED
1 skipped, 319 deselected in 0.04s
```

Solo 1 test tiene el marker `integration` (SMTP). El test de concurrencia con MySQL real
(`test_concurrency_alerts.py`) usa un `pytest.skip()` condicional propio, no el marker — por eso
`-m "integration"` no lo selecciona. **BLOCKER confirmado**: no hay contenedor `mysql` de ManttoAI
corriendo (`docker compose ps mysql` devuelve vacío; el único Docker activo en la máquina pertenece
a otro proyecto, `agrovoz`). No se intentó levantar MySQL porque el mandato explícito era no correr
Docker si no estaba ya disponible.

---

## 2. Backend — lint y formato

```
$ ruff check app/
All checks passed!

$ black --check app/
All done! ✨ 🍰 ✨
83 files would be left unchanged.
```

---

## 3. Frontend — lint

```
$ npm run lint
> eslint src --max-warnings=0
```
Sin output adicional = 0 errores y 0 warnings (el flag `--max-warnings=0` habría hecho fallar el
comando ante cualquier warning).

---

## 4. Frontend — Vitest

```
$ npm run test:unit
 ✓ src/api/admin.test.js (11 tests) 4ms
 ✓ src/utils/prediccion.test.js (20 tests) 5ms
 ✓ src/api/reportes.test.js (4 tests) 13ms
 ✓ src/context/AuthContext.test.jsx (1 test) 27ms
 ✓ src/pages/AdminPage.test.jsx (4 tests) 232ms
 ✓ src/components/mantenciones/MantencionForm.test.jsx (2 tests) 324ms
 ✓ src/components/equipos/EquipoForm.test.jsx (2 tests) 377ms
 ✓ src/api/umbrales.test.js (3 tests) 3ms
 ✓ src/utils/metrics.test.js (5 tests) 1ms
 ✓ src/hooks/usePolling.test.jsx (1 test) 134ms

 Test Files  10 passed (10)
      Tests  53 passed (53)
```

---

## 5. Frontend — build de producción

```
$ npm run build
vite v6.4.1 building for production...
✓ 1860 modules transformed.
dist/assets/index-ZDLqUUDi.js              245.02 kB │ gzip: 81.27 kB
✓ built in 1.12s
```
Sin errores ni warnings de build.

---

## 6. Frontend — Playwright E2E

Los specs mockean el backend completo vía `page.route()` (ver `frontend/tests/fixtures.js` y cada
`*.spec.js`), por lo que **no requieren backend real ni MySQL** — solo `vite preview` sirviendo el
build estático, que Playwright levanta solo (`webServer` en `playwright.config.js`). Se instalaron
los browsers (`npx playwright install --with-deps chromium firefox`, no estaban cacheados) y se
corrió la suite completa:

```
$ npx playwright test
Running 22 tests using 4 workers
  ✓ [chromium] home, dashboard, onboarding (x4), critical-flows (x3), operations — 11 specs
  ✓ [firefox]  mismos 11 specs
22 passed (13.2s)
```

Los 11 specs × 2 browsers (chromium, firefox) configurados en `playwright.config.js` dan 22 —
consistente.

---

## 7. Reconciliación de conteo de tests (backend + frontend)

| Fuente | Método | Resultado |
|---|---|---|
| Backend, funciones `def test_` crudas | `grep -rE "^[[:space:]]*def test_" tests/` | 313 |
| Backend, nodos collected por pytest | `pytest --collect-only -q` | 320 (313 funciones + 7 casos extra de 3 `@pytest.mark.parametrize` en 2 archivos) |
| Backend, ejecutados | pass+skip | 317 + 3 = 320 ✓ coincide |
| Frontend Vitest | reportado por vitest | 53 |
| Frontend Playwright | specs × browsers | 11 × 2 = 22 |
| **Total ejecutado hoy (backend + frontend unit + E2E)** | suma | **317 + 53 + 22 = 392 tests pasando**, 3 skipped documentados |

El "242" no se pudo reproducir bajo ningún patrón de grep razonable (con o sin indentación exacta,
incluyendo o excluyendo `async def`). No hay commits que hayan agregado archivos de test nuevos
desde el 10-jun-2026 (`git log --since="2026-06-10" --diff-filter=A -- 'tests/*.py'` → vacío), así
que el estado actual de 313 funciones/320 nodos ya existía cuando se hizo el commit que declara
"317 passed, 3 skipped, 0 failed". Se trata con alta confianza de un error de metodología en el
conteo de 242, no de una regresión de tests borrados.

---

## Findings

| Severidad | Ubicación | Hallazgo | Fix |
|---|---|---|---|
| MEDIUM | `frontend/package.json` (axios `^1.8.4`) | `npm audit` reporta 14 vulnerabilidades (1 low, 4 moderate, **8 high, 1 critical**) en dependencias, incluyendo múltiples CVEs de `axios` (SSRF, prototype pollution, auth bypass vía `validateStatus`) y uno crítico en `@babel/core` (arbitrary file read vía sourceMappingURL). Ninguna es explotable en runtime de producción hoy (son deps de build/HTTP client), pero el cliente HTTP del frontend es axios y varias CVEs afectan justamente el uso normal (interceptors, redirects). | Correr `npm audit fix` en una tarea separada, revisar breaking changes de axios major si aplica, y re-correr `npm run test:unit` + `npm run build` para confirmar que no rompe nada. Fuera de alcance de esta verificación (solo lectura). |
| LOW | `backend/tests/test_rate_limit_by_role.py:61` | Test permanentemente skippeado porque el rate limiting diferenciado por rol en `/dashboard/resumen` no está implementado. El test documenta un requisito no cumplido, no un bug de la suite. | Decisión de producto: implementar el rate limiting por rol o eliminar el test si se descarta el requisito. No es una acción de QA. |
| LOW | `backend/.venv` | El entorno virtual estaba roto al iniciar (symlink a Python 3.13 no instalado en `uv`), bloqueando cualquier corrida de pytest hasta recrearlo. No es un problema del repo (está gitignored) pero sí un gap de onboarding: el README no menciona qué hacer si `uv`/pyenv cambia de versión activa. | Opcional: documentar en `backend/README.md` que si el venv falla con symlink roto, recrear con `uv venv --python 3.11 .venv`. |
| INFO | `docker compose ps mysql` | Sin contenedor MySQL de ManttoAI corriendo en esta máquina (solo hay un contenedor de otro proyecto, `agrovoz`). Esto bloquea 1 test de concurrencia (`test_concurrency_alerts.py`) que requiere MySQL real + flag explícito. Reportado como blocker de entorno, no como fallo. | `docker compose up -d mysql` desde la raíz del repo si se quiere correr ese test específico. |

## Conclusión

No hay evidencia de tests rotos ni de regresión. La suite es genuinamente verde en todo lo
ejecutable sin MySQL: **317/317 backend (3 skips documentados y justificados) + 53/53 Vitest +
22/22 Playwright E2E, cobertura 85.15% sobre piso de 80%, ruff/black/eslint limpios, build de
producción sin errores.** El único blocker real es el test de concurrencia con MySQL, que requiere
levantar el contenedor `mysql` del proyecto — no se hizo por estar fuera del mandato de esta
verificación (no correr Docker si no estaba ya disponible).
