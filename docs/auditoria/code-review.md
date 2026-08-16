# Code Review — Backend (`backend/app/`)

> **Nota de vigencia:** este documento conserva la línea base histórica de la revisión.
> El estado de las correcciones locales y los gates todavía pendientes está en
> [`estado-implementacion.md`](estado-implementacion.md).

Revisión de solo lectura sobre `backend/app/` (routers, services, middleware, config,
dependencies, models). No se revisó frontend, tests, documentación ni CI/CD. Todos los
hallazgos citan `archivo:línea` verificado en el código leído; no hay hallazgos inferidos
de archivos que no se abrieron.

El backend está razonablemente bien estructurado (separación router/service, uso correcto
de SQLAlchemy 2.0 con `select()`, paginación con `Query(ge=, le=)` en casi todos los
endpoints, sanitización de fórmulas CSV, bcrypt con `rounds=12`, blacklist JWT por `jti`).
El problema no es el estilo: hay **un escalamiento de privilegios explotable sin
autenticación** (`POST /auth/register` acepta `rol: "admin"` del cliente), la **aislación
multi-tenant no está implementada a nivel de query** pese a existir toda la maquinaria de
tenant, **dos endpoints de administración devuelven 500 en su camino normal** por
violaciones de FK y por un hash inválido escrito a propósito, y el **módulo de métricas
nunca recolecta nada** porque su decorador no se aplica a ningún endpoint. Adicionalmente,
lógica de test vive dentro del código de producción en tres lugares distintos
(`/ready`, `dispatch_..._bg`, `create_lectura`), lo que es lo primero que nota un revisor
externo.

Sobre los tres puntos que se pidió confirmar en `main.py`: el doble montaje de routers es
real y tiene una consecuencia concreta (evasión de audit logging en `/iot`), pero **no**
produce bypass de autenticación — los routers admin declaran `require_role("admin")` en
ambos montajes. El branch de test en `/ready` es real pero **no enmascara una caída de DB
en producción**: la condición colapsa a `check_database_connection()` cuando
`app.state.testing_session_local` no existe, y ese atributo solo se asigna en
`tests/conftest.py:97,167`. El `import os` dentro de la función sí está en `main.py:241`.

## Hallazgos

| Severity | File:Line | Finding | Suggested fix |
|---|---|---|---|
| BLOCKER | `backend/app/services/auth_service.py:70` | `register_user` persiste `payload.rol` tal como llega del cliente. `UsuarioCreate` hereda `rol: Literal["admin","tecnico","visualizador"]` (`schemas/usuario.py:30`) y `POST /auth/register` (`routers/auth.py:30-41`) no declara ninguna dependencia de auth. Cualquier persona en internet obtiene una cuenta admin con `{"rol":"admin"}`, y con ella acceso a `/usuarios`, `/api-keys`, `/audit-logs`, `/chat/dataset-export` y `/chat/historial`. | Sacar `rol` de `UsuarioCreate` (crear un `UsuarioAdminCreate` con `rol` solo para `POST /usuarios`, que ya exige admin en `routers/usuarios.py:84`) y forzar `rol="visualizador"` en `register_user`. Test de regresión: registrar con `rol:"admin"` y aseverar que el usuario queda `visualizador`. |
| HIGH | `backend/app/services/dashboard_service.py:90-109` | La query del dashboard no filtra por `organizacion_id` pese a que `Equipo` lo declara (`models/equipo.py:54`) y su propio docstring dice que todos los queries deben filtrarse por la organización del usuario (`models/equipo.py:20-23`). Mismo caso en `services/equipo_service.py:14` y `services/lectura_service.py:32-42`. La única aislación existente es el chequeo header-vs-usuario de `dependencies.py:136-142`, que solo se activa si el cliente **envía** `X-Tenant-ID`: omitir el header desactiva el control por completo. | Resolver `organizacion_id` desde el usuario autenticado (no desde el header) y aplicarlo como `WHERE` en `list_equipos`, `list_lecturas`, `list_alertas` y `_build_dashboard_equipo_items`. `routers/onboarding.py:92-97` ya tiene el patrón correcto de verificación de propiedad. |
| HIGH | `backend/app/routers/usuarios.py:169-170` | `DELETE /usuarios/{id}` hace `db.delete(usuario)` sin tocar las filas que lo referencian. `audit_logs.usuario_id` (`models/audit_log.py:18`) y `api_keys.created_by_id` (`models/api_key.py:23`) son FK **sin** `ondelete`, y no hay `relationship()` desde `Usuario` hacia ellas que permita el nullify de SQLAlchemy. Cualquier usuario que haya hecho un solo POST tiene audit logs, así que el borrado falla con `IntegrityError` no capturado → HTTP 500. | Capturar `IntegrityError` y devolver 409 con mensaje accionable, o definir `ondelete="SET NULL"` en `audit_log.usuario_id` y decidir explícitamente qué pasa con las API keys creadas. Test: crear usuario, generar un audit log suyo, borrarlo. |
| HIGH | `backend/app/routers/usuarios.py:275` | El borrado RGPD escribe `usuario.password_hash = "ELIMINADO"`, que no es un hash bcrypt válido. Un login posterior con ese email llega a `verify_password` (`services/auth_service.py:39`) → `bcrypt.checkpw` levanta `ValueError: Invalid salt`, y `authenticate_user:83` no lo captura → HTTP 500 en un endpoint público en vez de 401. El chequeo de `is_active` está *después* de la verificación de password, así que no protege. `services/api_key_service.py:36` ya captura exactamente este `ValueError`, o sea que el modo de falla es conocido en el código. | Envolver `verify_password` en `try/except ValueError → return False`, o escribir un hash bcrypt de un valor aleatorio irrecuperable en lugar del literal. Test de regresión: anonimizar un usuario y luego intentar login con su email. |
| HIGH | `backend/app/routers/metrics.py:76-93` | `track_request_metrics` no se aplica a ningún endpoint (única ocurrencia del símbolo en todo `app/`), y `_record_metrics` (`metrics.py:96`) solo se llama desde ese decorador muerto. `RequestMetricsMiddleware` (`middleware/request_metrics.py:26-34`) únicamente loguea, nunca escribe en el store. Consecuencia: `GET /metrics/summary` siempre devuelve `total_requests: 0` y `endpoints: {}` (`metrics.py:189-192`) presentándolo como dato real. | O se registran las métricas desde `RequestMetricsMiddleware` llamando a `_record_metrics(request.url.path, elapsed)`, o se elimina el decorador y las claves Redis asociadas. Un endpoint de observabilidad que reporta ceros fabricados es peor que no tenerlo. |
| HIGH | `backend/app/middleware/rate_limit.py:33-36` | `get_real_ip` confía en `X-Forwarded-For` sin lista de proxies confiables y es la `key_func` global del limiter (`rate_limit.py:101`). Cualquier cliente que rote el header obtiene un bucket nuevo por request, anulando el rate limiting de `/auth/login` (`routers/auth.py:45`) y `/auth/register`, que es justo donde importa. | Confiar en `X-Forwarded-For` solo cuando la IP del peer pertenezca a la red del reverse proxy, o usar la implementación de proxy headers de uvicorn (`--proxy-headers --forwarded-allow-ips`) y quedarse con `get_remote_address`. |
| HIGH | `backend/app/config.py:35` | Los conjuntos de nombres de entorno "no-dev" están duplicados y no coinciden entre módulos: `config.py:35` = `{production, staging, prod}`, `config.py:136` = `{staging, stage, production, prod}`, `main.py:109` = `{production, staging, prod}`, `routers/auth.py:61-62` = `{staging, stage, production, prod}`. Con `APP_ENV=stage`: la validación de `SECRET_KEY` se salta (se autogenera una clave aleatoria por proceso, `config.py:53-55`) mientras las validaciones de DB/MQTT sí aplican, y `/docs` queda expuesto. Una clave por proceso además invalida los JWT emitidos por otro worker. | Extraer una única constante `NON_DEV_ENVS` (o un helper `is_production_like()`) en `config.py` e importarla en `main.py` y `routers/auth.py`. Test parametrizado sobre los cuatro nombres. |
| MEDIUM | `backend/app/main.py:154-228` | Doble montaje confirmado: 16 routers montados en raíz y en `/api/v1`, y `iot` montado **tres** veces (`main.py:162`, `216`, `217` — dos de ellas idénticas bajo `/api/v1`). Riesgo real: el audit middleware mapea `/api/v1/iot` pero no `/iot` (`middleware/audit.py:199`), así que la ingesta IoT por la ruta raíz **no queda auditada** mientras la misma operación bajo `/api/v1` sí. Secundario: cada endpoint aparece duplicado en OpenAPI con operation IDs colisionando. No hay bypass de auth: los routers admin repiten `require_role("admin")` en ambos montajes. | Montar cada router una sola vez bajo `API_V1_PREFIX` y ajustar los tests que dependen de la ruta raíz (son consumidores internos, no clientes legacy reales). Si algún montaje raíz debe sobrevivir, agregar las rutas faltantes a `_get_entity_from_path`. Eliminar en todo caso el montaje duplicado de `iot` en `main.py:217`. |
| MEDIUM | `backend/app/main.py:247-252` | `readiness_check` decide si consultar la DB comparando `check_database_connection` contra el centinela `ORIGINAL_CHECK_DATABASE_CONNECTION` (`main.py:51`) y consultando `hasattr(app.state, "testing_session_local")` — atributo que solo asigna `tests/conftest.py:97,167`. **No enmascara una caída real en producción** (la condición colapsa a `check_database_connection()`), pero son 8 líneas de lógica que fuera del test suite son un no-op, y el health check queda acoplado a cómo está escrito un fixture. | Dejar `components["db"] = check_database_connection()` y que el test parchee la función (es lo que ya hace `tests/test_health.py:18`). Eliminar el centinela de `main.py:51`. |
| MEDIUM | `backend/app/services/alerta_service.py:340-347` | Segunda instancia de lógica de test en producción: `dispatch_critical_email_notifications_bg` deriva `is_testing` de si `database_url` contiene `sqlite` y `:memory:`, y cambia de ejecución en thread a ejecución síncrona. El comportamiento en producción y en test difiere por inspección de un string de configuración. | Inyectar la estrategia de ejecución (parámetro `executor` o `run_sync: bool`) desde el caller; el test pasa la variante síncrona explícitamente. |
| MEDIUM | `backend/app/services/alerta_service.py:350-356` | Cada lote de alertas críticas lanza un `threading.Thread(daemon=True)` nuevo sin pool ni cola. Con `smtp_timeout=10` y `smtp_retry_attempts=3` (`config.py:93-94`), una ráfaga de alertas — el escenario esperado cuando un equipo se degrada — crea threads sin cota superior, cada uno además abriendo su propia sesión de DB (`alerta_service.py:300`). | Usar un `ThreadPoolExecutor` de tamaño fijo a nivel de módulo, o una cola con un worker único. |
| MEDIUM | `backend/app/services/mqtt_service.py:169` | `time.sleep(espera)` se ejecuta dentro de `_on_message`, que corre en el thread del loop de red de paho (`start_mqtt_subscriber:278` usa `loop_start()`). Si la DB se cae, cada mensaje bloquea ese loop hasta 3 s (1 s + 2 s), frenando la ingesta de **todos** los dispositivos y arriesgando la desconexión por keepalive del broker. | Sacar la persistencia del callback: `_on_message` encola el mensaje y un worker aparte hace los reintentos. |
| MEDIUM | `backend/app/services/mqtt_service.py:128` | Autorización asimétrica entre los dos caminos de ingesta. Por HTTP, `routers/iot.py:53` verifica que la API key corresponda al equipo (`api_key.device_id != str(payload.equipo_id)` → 403). Por MQTT, se resuelve `mac_address → equipo` y se persiste sin ninguna verificación de credencial de dispositivo: quien pueda publicar en el broker puede inyectar telemetría de cualquier equipo. El control compensatorio son las ACL de Mosquitto, que quedan fuera de esta revisión. | Validar la API key del dispositivo también en el camino MQTT (el payload puede incluirla, o mapear usuario MQTT → equipo), o documentar explícitamente que las ACL por topic del broker son el control de autorización. |
| MEDIUM | `backend/app/dependencies.py:96-124` | La verificación de blacklist de JWT construye un cliente Redis **nuevo en cada request autenticado** (sin pool) y falla abierto: `redis.Redis(...)` no conecta al construirse, así que `_redis_client` es truthy aunque Redis esté caído, y el `exists()` que falla se traga en `:122-124`. Resultado: con Redis inaccesible, los tokens revocados por logout o cambio de contraseña vuelven a ser válidos, en silencio. Mismo patrón de cliente por invocación en `routers/auth.py:110-116`. | Crear un cliente Redis a nivel de módulo (o un `ConnectionPool` compartido) y decidir explícitamente la política: fail-closed (401 si no se puede verificar) o fail-open documentado y con métrica/alerta. `password_changed_at` (`dependencies.py:150-153`) ya cubre el caso de cambio de contraseña sin Redis. |
| MEDIUM | `backend/app/services/lectura_service.py:80-127` | El bloque de recuperación de `IntegrityError` reimplementa la evaluación de umbrales importando tres funciones **privadas** de otro módulo (`_is_out_of_range`, `_resolve_alert_type`, `_resolve_threshold_target`, líneas 89-93) y duplicando en 48 líneas el algoritmo de `alerta_service.evaluate_thresholds:72-130`. Cualquier cambio de regla de negocio hay que hacerlo en dos lugares. Además el índice único que provocaba esos `IntegrityError` lo elimina `database.py:174-209`, así que el camino puede estar muerto en la práctica. | Exponer en `alerta_service` una función pública `evaluate_thresholds(db, lectura, skip_existing=True)` y llamarla desde ambos caminos. Verificar antes si el camino de recuperación sigue siendo alcanzable sin el índice único. |
| MEDIUM | `backend/app/services/api_key_service.py:60` | `key_prefix = plain_key[-12:]` guarda los **últimos** 12 caracteres del secreto (el comentario justifica "mayor entropía que 8", criterio invertido: para un identificador de display menos material secreto es mejor). Se persiste en claro y se devuelve por API (`schemas/api_key.py:18`, `routers/api_keys.py:38`). Una key es `mttk_` + 43 caracteres, así que se está exponiendo ~28% del secreto en la UI y en la DB. | Guardar el prefijo real (`plain_key[:12]`, que incluye el namespace `mttk_` y es lo que hacen Stripe/GitHub) y renombrar la columna acorde. La búsqueda de candidatos sigue funcionando igual. |
| MEDIUM | `backend/app/services/api_key_service.py:117-158` | `validate_api_key` es un duplicado casi literal de `get_api_key_user` en `dependencies.py:193-242`: misma búsqueda por sufijo, mismo loop bcrypt, mismo `last_used_at` con el mismo manejo de error. Dos copias de la ruta de autenticación de dispositivos. | Dejar `api_key_service.validate_api_key` como única implementación y que `get_api_key_user` sea un wrapper de FastAPI que la invoque. |
| MEDIUM | `backend/app/routers/metrics.py:240` | `GET /metrics/health-detailed` devuelve `str(exc)` de la excepción SQLAlchemy cruda al cliente (y lo mismo con Redis en `:252`). Los mensajes de DBAPI suelen incluir host, puerto, usuario y a veces la cadena de conexión. El router exige autenticación (`main.py:220-228`) pero no rol, así que un `visualizador` ve infraestructura interna. | Loguear la excepción completa y devolver un mensaje genérico (`"database unreachable"`), o restringir el endpoint a `require_role("admin")`. |
| MEDIUM | `backend/app/services/chat_service.py:80` | `consultar_ollama` es `async` pero llama `get_dashboard_summary(db)` de forma síncrona, que ejecuta cuatro subqueries con window functions (`dashboard_service.py:90-109`) bloqueando el event loop. El mismo patrón en `routers/chat.py:39-40` (`db.commit()`), `:55` y `:86` — todos endpoints `async def` con SQLAlchemy síncrono. | Definir los endpoints de chat como `def` (FastAPI los corre en threadpool) o envolver el trabajo de DB en `run_in_threadpool`, como ya hace `middleware/audit.py:130`. |
| MEDIUM | `backend/app/routers/chat.py:55` | `GET /chat/dataset-export` hace `.all()` sobre la tabla completa de `MensajeChat` sin límite, serializa cada fila a JSON en memoria y las une en un solo string. Es admin-only, pero el consumo de memoria crece sin cota con el historial. Relacionado: `/chat/historial` acepta `limit: int = 100` sin `Query(le=...)` (`chat.py:79-80`), el único endpoint del backend sin cota — todos los demás usan `Query(ge=, le=)`. | Paginar el export con `yield_per` + `StreamingResponse`, y acotar `limit` con `Query(default=100, ge=1, le=500)`. |
| MEDIUM | `backend/app/services/dashboard_service.py:15-17` | El cache del dashboard es estado mutable a nivel de módulo (`_cached_summary`, TTL 5 s) sin clave por usuario ni por organización, y sin lock pese a que FastAPI sirve endpoints `def` en un threadpool. Hoy devuelve datos globales a todos; en el momento en que se implemente el filtrado por tenant (hallazgo HIGH de arriba), este cache filtra datos de una organización a otra. | Cachear por clave (`organizacion_id`) o eliminar el cache — la query ya está optimizada con window functions y el `/dashboard/resumen` no es tan caliente como para justificar estado global. |
| MEDIUM | `backend/app/database.py:109-145` | `_dedupe_alertas_by_logical_key` contiene un `DELETE` masivo sobre `alertas` y **no se llama desde ninguna parte del código de producción** (única referencia fuera de su definición: `tests/test_database_runtime_fixes.py`). Código muerto destructivo que un test mantiene vivo. | Eliminar la función y su test, o si la deduplicación se necesita, invocarla explícitamente desde una tarea de mantenimiento — nunca desde el arranque. |
| MEDIUM | `backend/app/routers/equipos.py:145-199` | `create_equipo_with_umbrales` construye modelos ORM, hace `flush`/`commit`/`rollback` e importa `Equipo` y `Umbral` dentro del cuerpo de la función (`:155-156`), todo en la capa router. `CLAUDE.md` fija la convención "routers for HTTP, services for business logic", y el resto del archivo la respeta delegando en `equipo_service`. | Mover la transacción completa a `equipo_service.create_equipo_with_umbrales(db, payload)` y dejar el router en una sola llamada. |
| MEDIUM | `backend/app/routers/equipos.py:202-245` | `POST /equipos/auto-register` es público y acepta cualquier token de provisioning válido por 1 hora (`equipos.py:60-69`). El token no tiene `jti` ni marca de un solo uso, así que quien lo capture (va en un QR) puede crear equipos de forma repetida durante toda su ventana. Es además el único endpoint de escritura sin `@limiter.limit` propio. | Agregar `jti` al token, invalidarlo tras el primer uso (Redis, igual que la blacklist de logout) y aplicar un rate limit explícito. |
| LOW | `backend/app/main.py:241` | `import os` dentro del cuerpo de `readiness_check`, con `redis` y `socket` también importados inline (`:261`, `:274`). Es un patrón repetido en el backend: `config.py:53,132`, `dependencies.py:100`, `routers/equipos.py:155,232`, `routers/onboarding.py:84`, `services/lectura_service.py:87-93`, `services/alerta_service.py:337`, `middleware/rate_limit.py:72,82`. Los imports opcionales (`redis`, `paho`) tienen justificación; `os` y los modelos propios no. | Subir al top del módulo todo lo que no sea una dependencia opcional. `ruff` con la regla `PLC0415` lo detecta (ya hay un `# noqa: PLC0415` en `middleware/tenant.py:32`, o sea que la regla está activa). |
| LOW | `backend/app/models/usuario.py:37` | Comentario con texto en chino incrustado: `(nullable permite null cuando已完成)`. Único caracter CJK en todo `backend/app/`. Es lo primero que salta en una lectura externa del código. | Reemplazar por `cuando está completado`. |
| LOW | `backend/app/services/chat_service.py:126-135` | Diez líneas de código comentado (el bloque de few-shot prompting deshabilitado) dentro de `consultar_ollama`. El historial de git ya guarda esto. | Eliminar el bloque. |
| LOW | `backend/app/services/chat_service.py:58` | Logging con f-string (`logger.info(f"...")`), también en `:146` y `:157`, mientras el resto del backend usa lazy `%s`. Evalúa el string siempre, incluso con el nivel desactivado. | `logger.info("[CHATBOT] Respuesta desde regla: %s", keyword)`. |
| LOW | `backend/app/services/chat_service.py:14-33` | `REGLAS_MANTENIMIENTO` duplica valores completos para manejar tildes (`vibracion`/`vibración`, `grafico`/`gráfico`, `agricola`/`agrícola`) y repite la misma respuesta literal en tres claves (`probabilidad`, `falla`, `riesgo`). Cambiar un texto exige tocar hasta tres entradas. | Normalizar el mensaje del usuario con `unicodedata` (ya se usa en `services/report_service.py:72`) y mapear varias claves a una constante compartida. |
| LOW | `backend/app/routers/metrics.py:284` | `POST /metrics/reset` verifica el rol inline con `current_user.rol != "admin"` en vez de usar `require_role("admin")` como el resto del backend, y la comparación es sensible a mayúsculas mientras `dependencies.py:176` normaliza con `.lower()`. Un rol `"Admin"` pasaría `require_role` y fallaría acá. | Reemplazar por `Depends(require_role("admin"))` en la firma. |
| LOW | `backend/app/routers/chat.py:3` | `from typing import List` con `List[...]` en `:77` mientras `:83` usa `list[MensajeChat]` en el mismo archivo; y `:28` anota `-> dict` cuando la función retorna `ChatMessageResponse`. | Usar `list[...]` y corregir la anotación de retorno. |
| LOW | `backend/app/routers/equipos.py:149` | `current_user: Usuario = Depends(require_role("admin","tecnico"))` se declara en la firma pero nunca se usa en el cuerpo, y la misma dependencia ya está en el decorador (`:143`). Como cada llamada a `require_role(...)` produce un closure distinto, FastAPI no la deduplica y `role_checker` corre dos veces. | Eliminar el parámetro. |
| LOW | `backend/app/config.py:26` | `api_prefix: str = ""` no se referencia en ninguna parte de `app/` (el prefijo real está hardcodeado en `main.py:118`). Campo de configuración muerto. | Eliminarlo o usarlo en `main.py:118`. |
| LOW | `backend/app/middleware/rate_limit.py:100-105` | La construcción del limiter a nivel de módulo llama `_resolve_storage_uri()`, que abre una conexión Redis y hace `ping()` con timeout de 2 s **en tiempo de import**. Importar `app.main` (tests, scripts, `alembic`) dispara I/O de red. | Inicializar el storage de forma perezosa en `setup_rate_limiting(app)`. |
| LOW | `backend/app/services/lectura_service.py:137` | `alerta_ids = [a.id for a in alertas_creadas ...]` se evalúa después de `db.commit()` (`:79`/`:127`). Con `expire_on_commit=True` (default, `database.py:36` no lo desactiva), cada acceso a `a.id` y `a.nivel` dispara un SELECT de refresco: N+1 pequeño pero real en el camino de ingesta. | Capturar los ids antes del commit, o construir el sessionmaker con `expire_on_commit=False`. |
| INFO | `backend/app/main.py:109` | `_docs_enabled` deshabilita `/docs`, `/redoc` y `/openapi.json` cuando `app_env` está en `{production, staging, prod}`. Se reporta sin recomendación: la decisión de exponer la documentación para una demo a reclutadores es del autor. Nota técnica: si se decide exponerla, el conjunto de nombres de entorno debe unificarse primero (ver el hallazgo HIGH de `config.py:35`), porque hoy `APP_ENV=stage` ya deja `/docs` abierto de forma no intencional. | — |

## Resumen

- **1 BLOCKER**, **7 HIGH**, **16 MEDIUM**, **11 LOW**, 1 informativo.
- El BLOCKER es explotable sin autenticación con un solo `curl` y otorga rol admin.
- Los dos HIGH de `routers/usuarios.py` (500 en `DELETE /usuarios/{id}` y 500 en login tras
  anonimización RGPD) son fallas del camino normal, no de bordes: se reproducen con el flujo
  documentado del propio endpoint.
- Tres módulos distintos contienen ramas condicionadas por estado de test
  (`main.py:247-252`, `alerta_service.py:340-347`, `lectura_service.py:82`); es el patrón que
  más rápido se identifica en una lectura externa del código.

## Verificación

Comandos para reproducir los hallazgos principales (contra un backend local en `:8000`):

```bash
# BLOCKER — escalamiento de privilegios sin autenticación
curl -s -X POST localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"pwn","email":"pwn@test.cl","password":"Abcd1234!","rol":"admin"}' | jq .rol
# esperado hoy: "admin"

# HIGH — 500 al borrar un usuario con audit logs
# (crear usuario, hacer un POST autenticado como él, luego:)
curl -s -o /dev/null -w '%{http_code}\n' -X DELETE localhost:8000/usuarios/<id> \
  -H "Authorization: Bearer <admin_token>"

# HIGH — 500 al intentar login de un usuario anonimizado por RGPD
curl -s -X DELETE localhost:8000/usuarios/<id>/datos-personales -H "Authorization: Bearer <admin_token>"
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"eliminado_<id>@anonimizado.manttoai","password":"loquesea"}'

# HIGH — métricas siempre en cero
curl -s localhost:8000/metrics/summary -H "Authorization: Bearer <token>" | jq '.api'

# HIGH — bypass de rate limit rotando X-Forwarded-For
for i in $(seq 1 30); do
  curl -s -o /dev/null -w '%{http_code} ' -X POST localhost:8000/auth/login \
    -H "X-Forwarded-For: 10.0.0.$i" -H 'Content-Type: application/json' \
    -d '{"email":"a@b.cl","password":"x"}'
done  # sin 429 pese al límite de 10/minute

# MEDIUM — ingesta IoT por raíz no auditada vs /api/v1
# publicar en ambas rutas y comparar filas nuevas en audit_logs
```

Verificación estática ya ejecutada en esta revisión:

```bash
rg -n "track_request_metrics" backend/app/          # 1 sola línea: la definición
rg -c "_dedupe_alertas_by_logical_key" -g '*' .     # solo definición + su test
rg -n "testing_session_local\s*=" backend/          # solo tests/conftest.py y tests/*
rg -n '[\p{Han}]' backend/app/                      # models/usuario.py:37
```
