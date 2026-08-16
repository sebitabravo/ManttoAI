# Estado de implementación de la auditoría

Fecha de esta revisión: **2026-08-16**.

Los documentos `code-review.md`, `security.md`, `qa.md`, `deploy.md` y `ux.md`
son la línea base de la auditoría. Este registro separa lo corregido en el
workspace de lo que todavía necesita un proveedor externo o una decisión de
producto.

## Hallazgos corregidos

| Área | Estado | Evidencia local |
|---|---|---|
| Registro público con `rol=admin` | **Corregido** | `UsuarioSelfRegister` fuerza `visualizador`; regresión en `tests/test_auth.py` |
| Script de admin con credenciales embebidas | **Corregido** | `create_admin.py` exige entorno local y contraseña por variable/prompt; el seed rechaza contraseñas publicadas |
| Hash inválido después de anonimización RGPD | **Corregido** | hash bcrypt aleatorio + usuario inactivo; login devuelve 401 |
| Aislación por organización | **Corregido** | alcance desde JWT en `db.info`; equipos, lecturas, alertas, dashboard, umbrales, mantenciones, predicciones, reportes, usuarios, API keys y auditoría |
| Borrado de usuario con FK dependientes | **Corregido** | limpia API keys/mensajes, desvincula audit logs y traduce `IntegrityError` a 409 |
| Métricas siempre en cero | **Corregido** | middleware registra duración real; Redis es opcional; endpoints operacionales son admin-only |
| `X-Forwarded-For` falsificable | **Corregido** | solo se acepta desde `TRUSTED_PROXY_IPS`; sin proxy confiable se usa el peer TCP |
| Guardas inconsistentes de `APP_ENV`/CORS/docs/cookies | **Corregido** | entornos desconocidos fallan cerrado y se comparte `NON_DEV_ENVS` |
| Rate limiting por rol del dashboard | **Corregido** | admin 10/min, técnico 6/min, visualizador 3/min; test antes omitido reactivado |
| Readiness acoplado al fixture de tests | **Corregido** | `/ready` siempre consulta DB y dependencias configuradas |
| Contraseña Redis separada de `REDIS_URL` | **Corregido** | readiness, blacklist JWT, logout y métricas pasan `REDIS_PASSWORD` a redis-py; regresión de Compose |
| Revocación JWT sin Redis | **Corregido** | `revoked_tokens` persiste el `jti` hasta su expiración; logout y `get_current_user` tienen regresión sin Redis; migración reversible |
| Advisories de React Router | **Corregido** | `react-router-dom@7.18.2`; `npm audit --omit=dev --audit-level=moderate` devuelve 0 vulnerabilidades y lint/unit/build/E2E siguen verdes |
| Búsqueda de API keys por sufijo | **Corregido** | se persiste y busca el prefijo real de 12 caracteres |
| Dependencia JWT desactualizada | **Corregido** | `python-jose` fue reemplazado por `PyJWT==2.13.0`; regresión parametrizada en `tests/test_jwt_provider.py` |
| Cache global del dashboard | **Corregido** | eliminado para no cruzar datos entre organizaciones |
| Cold start y estados vacíos del frontend | **Corregido** | timeout configurable de 60 s, mensaje de despertar y estado de error sin ceros ficticios; regresiones en `frontend/src/pages/DashboardPage.test.jsx` y `LoginPage.test.jsx` |
| Provisioning sin MAC asociada y replay del token | **Corregido** | token ligado a MAC/tenant, fila persistida por `jti`, consumo bloqueado en la misma transacción y límite 10/h; regresión cubre replay tras borrar el equipo |
| Callback MQTT bloqueante | **Corregido** | cola acotada + worker de persistencia fuera del loop Paho |
| Chat sin límites de salida y reglas duplicadas por tildes | **Corregido** | historial máx. 500, export máx. 10.000 y normalización Unicode |
| Métricas incorrectas del load test | **Corregido** | respeta `requests_per_user`, conserva la clave de cada task y tiene regresión async |
| Cuenta demo compartida mutable | **Corregido** | `Usuario.is_demo` bloquea perfil/contraseña en backend, el seed exige password externa y el frontend deshabilita esos controles |
| Acceso de reclutador sin credenciales publicadas | **Corregido localmente** | `LoginPage` muestra **Usar cuenta demo** solo con `VITE_DEMO_EMAIL` y `VITE_DEMO_PASSWORD`; el botón rellena una cuenta read-only y no autoingresa. Falta verificar el flujo en un deployment público |
| Blueprint Render Free con seed | **Corregido localmente** | Render Free no admite `preDeployCommand`; se eliminó del blueprint y `Dockerfile.render` ejecuta el seed idempotente antes de Uvicorn. La imagen construida y el arranque contra MySQL local respondieron `/health` 200 |
| Secretos locales dentro de contextos Docker | **Corregido** | `backend/.dockerignore` y `frontend/.dockerignore` excluyen `.env`/`.env.*`; la imagen Compose reconstruida ya no contiene `/app/.env`; regresiones en `tests/test_render_deploy_config.py` |
| Bootstrap Alembic en base vacía | **Corregido localmente** | `alembic/env.py` crea el esquema vigente y registra `d8e9f0a1b2c3` cuando no existen tablas de aplicación; la regresión cubre upgrade, segundo upgrade y downgrade persistido en `tests/test_alembic_bootstrap.py` |
| Screenshots duplicados en dos rutas | **Corregido** | `screenshots/` queda como ruta canónica; `docs/manual-usuario.md` fue actualizado y se eliminó el segundo directorio de capturas |
| Doble montaje de routers y superficie OpenAPI | **Corregido** | Los routers operativos se montan una sola vez bajo `/api/v1`; `/health`, `/ready` y `/legal/*` quedan como excepciones documentadas; regresión en `tests/test_api_versioning.py` |
| Simulador MQTT incompatible con el contrato por MAC | **Corregido** | El seed asigna MACs demo, `make simulate` publica `{mac_address}`, las credenciales se leen dentro del contenedor y el flujo broker → backend → MySQL fue verificado con 24 mensajes |
| Logout afirmando éxito si falla la revocación JWT | **Corregido** | El endpoint devuelve 503 ante `SQLAlchemyError`; regresión en `tests/test_auth.py` |

## Hardening de mantenibilidad cerrado en esta iteración

Estos cambios no reabren los hallazgos históricos: son correcciones locales
adicionales verificadas con regresiones enfocadas y la suite completa.

| Hallazgo | Estado | Evidencia |
|---|---|---|
| Estrategia SMTP implícita por SQLite y threads sin cota | **Corregido** | `alerta_service.py` recibe `run_inline` explícito y usa `ThreadPoolExecutor(max_workers=4)`; regresiones en `tests/test_alertas.py` |
| Validación de API key duplicada | **Corregido** | `dependencies.py` delega a `api_key_service.validate_api_key`; regresión en `tests/test_api_keys.py` |
| Fallback de umbrales duplicado tras `IntegrityError` | **Corregido** | `lectura_service.py` reutiliza `evaluate_thresholds`; regresión en `tests/test_lectura_service.py` |
| Helper destructivo de deduplicación sin callers | **Corregido** | Eliminado `_dedupe_alertas_by_logical_key` y sus tests muertos |
| Transacción ORM de full setup en el router | **Corregido** | `equipo_service.create_equipo_with_umbrales`; regresiones en `tests/test_equipos.py` |
| SQL síncrono dentro de endpoints async de chat | **Corregido** | Consultas, persistencia, export e historial usan `run_in_threadpool`; regresión en `tests/test_chat.py` |
| Cliente Redis de revocación creado por request | **Corregido** | Cliente lazy compartido entre `dependencies.py` y `routers/auth.py`; su pool se reutiliza y la regresión está en `tests/test_auth.py` |
| Secret scanning del worktree | **Verificado** | Gitleaks no encontró secretos en archivos no ignorados; las detecciones actuales están limitadas a `.env` locales y artefactos de agentes ignorados. El historial conserva un falso positivo de un fixture antiguo, sin reescritura destructiva. |
| Script de demo exponiendo JWT en consola | **Corregido** | `scripts/demo-defensa.sh` valida el login sin imprimir la respuesta ni fragmentos del token; `bash -n` y el scan específico de salida pasan. |

## Deuda residual no bloqueante y límites del prototipo

| Residual | Tratamiento actual |
|---|---|
| MQTT no tiene identidad criptográfica por dispositivo dentro del payload | El broker exige credenciales y queda en red interna local; para MQTT público se requiere ACL por topic o credencial por nodo antes de producción. No se inventó un protocolo nuevo para el prototipo académico. |
| Redis de revocación es opcional | La fuente autoritativa es `revoked_tokens` en MySQL; el cliente Redis lazy compartido solo acelera una verificación adicional y puede omitirse en Render single-process. Si Redis falla, la revocación persistente sigue aplicándose. |
| Login entrega también `access_token` en el body | Se conserva por compatibilidad con CLI/API; el frontend usa cookie `HttpOnly` y no persiste el token. |
| Transición Alembic desde una base no versionada | Se estampa automáticamente solo cuando tablas y columnas coinciden exactamente con `Base.metadata`; un esquema parcial se rechaza antes de ejecutar migraciones históricas. MySQL 8.0.41 efímero pasó `upgrade head` → `downgrade base`, incluyendo el manejo de FKs/índices; la validación contra Aiven y una copia representativa de datos todavía sigue pendiente. |
| Crecimiento de telemetría en Aiven Free | **Mitigado localmente** | `TELEMETRY_RETENTION_DAYS=30` en el blueprint y purga idempotente por ciclo del simulador; desarrollo mantiene `0` para no borrar fixtures automáticamente |

## Estado operativo del demo

- `MQTT_ENABLED=false` permite que el simulador persista lecturas directo en la
  base de datos cuando Render no tiene broker MQTT.
- `backend/Dockerfile.render` genera el artefacto ML ignorado por Git y copia el
  seed al contenedor; como Render Free no tiene `preDeployCommand`, el comando
  de arranque lo ejecuta de forma idempotente antes de Uvicorn.
- `scripts/setup_env.sh` genera y conserva secretos locales; no se distribuyen
  contraseñas conocidas en el repo.
- El simulador directo, el seed local, el load test, la cuenta demo de solo
  lectura y la revocación persistente tienen regresiones propias; el runner
  raíz (`./test.sh`) quedó en **370 passed, 3 skipped** (373 tests
  recolectados). `make test` reportó **86 %** de cobertura. Los skips son
  explícitos: SMTP real requiere `RUN_REAL_SMTP_TEST=true`, concurrencia
  requiere MySQL real con `RUN_DB_CONCURRENCY_TESTS=1` y el roundtrip MySQL de
  Alembic requiere una base efímera con `RUN_MYSQL_ALEMBIC_TESTS=1`; no son
  fallos del código ni evidencia de providers públicos.
- `test.sh` es el runner raíz ejecutable que detecta Codex QA; el gate real se
  ejecutó sobre el workspace actual y terminó con código 0. `make test` conserva
  la corrida completa con cobertura para desarrollo.
- El smoke test Compose se ejecutó completo el **2026-08-16**: backend, frontend,
  MySQL, Redis, Mosquitto, simulador MQTT, alertas, predicción y Mailpit
  respondieron correctamente. Después de cargar el modelo, `docker stats` midió
  **313,6 MiB** para el backend; queda bajo el umbral local de mitigación de
  450 MiB, pero la medición no sustituye una prueba en el límite real de Render.
- La imagen de `backend/Dockerfile.render` también se construyó para
  `linux/amd64` y arrancó con `--memory=512m --memory-swap=512m`: `/health` y
  `/ready` respondieron `200`, `docker stats` reportó **204,3 MiB** y el proceso
  mostró `VmRSS=220736 kB`. La base fue SQLite aislada; Aiven sigue pendiente.
- La verificación final de Compose devolvió `/health` 200 y `/ready` 200 con
  `db=true`, `redis=true` y `mqtt=true`; todos los servicios quedaron healthy.
- En el mismo Compose, `make seed` creó `demo@manttoai.local`; `/auth/me`
  devolvió `is_demo=true` y sus mutaciones de perfil/contraseña devolvieron
  **403**. Un provisioning real contra MySQL devolvió **201** en el primer
  uso y **409** en el replay del mismo JWT.
- Frontend: **59 tests unitarios**, lint y build Vite verdes; Playwright quedó en
  **22/22** para Chromium y Firefox. Son pruebas locales con fixtures/mocks, no
  una prueba de MySQL, DNS o servicios públicos.
- `npm audit --omit=dev --audit-level=moderate` queda en código 0 después de
  actualizar `react-router-dom` a **7.18.2** sin scripts de lifecycle. Lint,
  59 tests unitarios, build y 22/22 Playwright fueron repetidos después del
  cambio.
- `.github/workflows/deploy.yml` dejó de crear `.env` desde una plantilla y
  verifica `/health` y `/ready` en el host remoto. El workflow no se ejecutó
  contra un VPS en esta revisión.

## Pendientes explícitos

| Pendiente | Motivo | Gate requerido |
|---|---|---|
| Validación MySQL/Aiven de transición `create_all` → Alembic | MySQL 8.0.41 efímero ya cubre `upgrade head` → `downgrade base` y reveló/corrigió un error de FK/índice; falta ejecutar el mismo camino contra Aiven y una copia representativa de datos | respaldo, inspección MySQL/Aiven, constraints/datos reales y smoke autenticado antes de retirar los flags runtime |
| MySQL/Aiven, SMTP real, MQTT externo y DNS | No son reproducibles desde SQLite/local sin credenciales | integración autenticada y smoke público |
| URL pública Render/Vercel | `render.yaml` y `vercel.json` son configuración; Render responde 404 y el proyecto Vercel auto-enlazado `frontend` tiene ajustes/despliegues ajenos a ManttoAI | crear explícitamente los servicios ManttoAI, configurar secretos y verificar navegador |
| Metadata de vitrina GitHub | Descripción y topics ya están configurados; `homepageUrl` sigue vacío porque no existe una URL pública verificada y el último push remoto es histórico | completar homepage solo después de verificar el deployment y publicar el estado actual mediante el flujo Git autorizado |

## Regla de publicación

No anunciar una URL ni afirmar despliegue hasta comprobar desde fuera del
workspace `/health`, `/ready`, login, dashboard con lecturas, alerta,
predicción, logout y la cookie same-origin desde Vercel.
