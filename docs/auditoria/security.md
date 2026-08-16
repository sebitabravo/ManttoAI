# Auditoría de seguridad — Exposición pública del prototipo (demo para reclutadores)

> **Nota de vigencia:** este documento conserva la línea base histórica de la auditoría.
> Las correcciones locales y los gates todavía pendientes se registran en
> [`estado-implementacion.md`](estado-implementacion.md); no usar este resumen como estado
> actual sin contrastarlo con ese documento.

> **DISCLAIMER**: Esta es una evaluación de asesoría, no un test de penetración certificado.
> Alcance: autenticación por cookie + CSRF, CORS, rate limiting, workflow de deploy, modelo
> de permisos para una cuenta demo, e higiene de secretos. No cubre calidad de código,
> tests ni UX de frontend. Revisión estática, sin ejecución contra sistemas vivos.

## Resumen ejecutivo

El diseño de autenticación es sólido en lo estructural: cookie `HttpOnly`, double-submit CSRF
correctamente verificado en métodos mutantes, JWT `HS256` con `algorithms` fijado explícitamente,
bcrypt con `rounds=12`, invalidación de tokens emitidos antes de un cambio de contraseña, y RBAC
por ruta que sí deja al rol `visualizador` como sólo-lectura sobre equipos, lecturas, alertas,
umbrales, mantenciones y predicciones. Sin embargo, **el sistema no es apto para exposición
pública hoy** por un defecto único y decisivo: `POST /auth/register` es un endpoint sin
autenticación que acepta el campo `rol` del cuerpo de la petición, de modo que cualquier persona
en internet puede crearse una cuenta `admin` y obtener control total de la instancia —
incluyendo gestión de usuarios, API keys y audit logs. El propio test
`backend/tests/test_auth.py:15-38` documenta ese comportamiento como esperado.

Sobre ese hallazgo se apilan tres problemas de configuración que degradan las demás defensas:
el rate limiting usa `X-Forwarded-For` sin filtrar como clave, lo que permite evadir el límite
de 10 intentos/minuto de login rotando un header; cualquier valor de `APP_ENV` fuera del
conjunto literal `{staging, stage, production, prod}` desactiva en silencio la validación de
`SECRET_KEY`, el flag `Secure` de la cookie y el ocultamiento de `/docs`; y el logout depende de
Redis para revocar el JWT, por lo que en el despliegue free-tier propuesto (sin Redis) el token
sigue siendo válido hasta 4 horas después de cerrar sesión.

Adicionalmente, hay un **bloqueante funcional** para la topología propuesta: con el SPA en
`*.vercel.app` y el backend en `*.onrender.com` el navegador considera la petición cross-site,
y la cookie emitida con `SameSite=Lax` no se adjuntará. El login simplemente no funcionará; la
corrección apresurada habitual (`SameSite=None`) exige `Secure` obligatorio y reduce el CSRF a
depender exclusivamente del double-submit token, por lo que conviene decidirlo de forma
consciente y no en caliente.

En higiene de secretos el repositorio está limpio: no hay claves reales versionadas, los
`.env*` están correctamente ignorados y el firmware ESP32 usa marcadores `REEMPLAZAR_*`. La
excepción es `backend/create_admin.py`, un script versionado que crea un administrador con
contraseña embebida y sin ninguna comprobación de entorno.

**Veredicto: no desplegar públicamente hasta corregir SA-001, SA-002, SA-003 y SA-004.**

## Hallazgos

| # | Severidad | Archivo:Línea | Hallazgo | Corrección recomendada |
|---|---|---|---|---|
| SA-001 | CRITICAL | `backend/app/routers/auth.py:30-41`, `backend/app/services/auth_service.py:66-71`, `backend/app/schemas/usuario.py:30` | `POST /auth/register` es público (sin `Depends`) y `register_user` asigna `rol=payload.rol`, con `rol` declarado en `UsuarioBase` como `Literal["admin","tecnico","visualizador"]`. Cualquier anónimo se registra como `admin`. Confirmado por `backend/tests/test_auth.py:15-38`, que envía `"rol": "admin"` y espera 201. | Eliminar `rol` del schema de auto-registro (crear un `UsuarioSelfRegister` que fuerce `visualizador`), o deshabilitar `/auth/register` en el despliegue público y crear las cuentas sólo vía `POST /usuarios` (que ya exige `admin`). Actualizar el test para asertar que el rol solicitado se ignora. |
| SA-002 | HIGH | `backend/app/config.py:35`, `backend/app/config.py:136`, `backend/app/main.py:109`, `backend/app/routers/auth.py:61-62,70-71` | Los guardas de producción se activan por comparación literal contra `{"production","staging","prod"}` / `{"staging","stage","production","prod"}`. Un `APP_ENV` como `demo`, `render` o `Production` (main.py:109 ni siquiera normaliza mayúsculas) deja pasar `SECRET_KEY` vacío, emite las cookies sin `Secure` y publica `/docs`, `/redoc` y `/openapi.json`. Con `SECRET_KEY` vacío, config.py:53-55 genera una clave aleatoria **por proceso**: con más de un worker, los tokens de un worker son inválidos en otro. | Reemplazar los conjuntos literales por un `Literal["development","staging","production"]` validado en `Settings`, que rechace cualquier otro valor en el arranque. Fallar cerrado ante `APP_ENV` desconocido en vez de asumir desarrollo. |
| SA-003 | HIGH | `backend/app/middleware/rate_limit.py:30-36`, `backend/app/middleware/rate_limit.py:101` | `get_real_ip` devuelve el primer valor de `X-Forwarded-For` sin validar la cadena ni la IP del proxy, y es el `key_func` global del limiter. Un atacante que envíe `X-Forwarded-For: <aleatorio>` en cada petición obtiene un bucket nuevo cada vez, anulando el límite de `10/minute` sobre `/auth/login` (`auth.py:45`) y el límite global. No hay bloqueo de cuenta tras N fallos, así que el rate limit es la única defensa contra fuerza bruta. | Confiar en `X-Forwarded-For` sólo cuando el peer inmediato esté en una lista de proxies conocidos, y tomar el último salto no confiable en vez del primero. En Render, usar el header propio de la plataforma. Añadir bloqueo temporal por cuenta tras fallos consecutivos. |
| SA-004 | HIGH | `backend/create_admin.py:7-8` | Script versionado que inserta `admin@mantto.ai` con la contraseña `admin123` en texto plano, con rol `admin`, sin comprobar `APP_ENV` ni pedir confirmación. Ejecutarlo una vez contra la base desplegada deja credenciales de administrador públicas (están en el repositorio, que será público para los reclutadores). La contraseña además no cumple la política de complejidad que sí exige el registro. | Eliminar el archivo del repositorio, o convertirlo en un script que lea la contraseña de una variable de entorno / prompt y aborte si `APP_ENV` no es de desarrollo. |
| SA-005 | MEDIUM | `backend/app/routers/auth.py:60,69`, `frontend/src/api/client.js:24` | Cookies emitidas con `samesite="lax"`. En la topología propuesta (SPA en Vercel, API en Render) las peticiones son cross-site y el navegador no adjuntará la cookie pese a `withCredentials: true`. **Bloqueante funcional**, y la corrección apresurada (`SameSite=None`) obliga a `Secure` y deja el CSRF apoyado sólo en el double-submit token. | Preferir servir SPA y API bajo el mismo sitio (subdominio del mismo dominio + `domain=`) y mantener `Lax`. Si se mantienen dominios distintos, cambiar a `samesite="none"` **con `secure=True` incondicional** y verificar que el chequeo CSRF de `dependencies.py:72-80` siga activo. |
| SA-006 | MEDIUM | `backend/app/routers/auth.py:104-118`, `backend/app/dependencies.py:95-124` | El logout revoca el JWT escribiendo `blacklist:{jti}` en Redis; si `redis` no está disponible ambos bloques degradan silenciosamente (`except Exception: pass`). Sin Redis en el free-tier, el logout sólo borra la cookie del navegador: un token capturado (log, historial, extensión) sigue siendo válido hasta 4 h (`auth_service.py:18`). | Para el demo, reducir `ACCESS_TOKEN_EXPIRE_HOURS` a 1 h o menos. Alternativa sin Redis: persistir los `jti` revocados en MySQL, que ya está disponible. Documentar explícitamente que sin Redis el logout no es revocación. |
| SA-007 | MEDIUM | `backend/app/routers/auth.py:134-149`, `backend/app/routers/auth.py:152-187` | Un usuario `visualizador` —el rol previsto para la cuenta demo— puede cambiar su propia contraseña y editar su perfil. Con una cuenta demo compartida, el primer visitante que use `POST /auth/change-password` deja fuera a todos los siguientes (y `dependencies.py:150-153` invalida además todos los tokens emitidos antes del cambio). | Bloquear `change-password` y `PUT /profile` para la cuenta demo: añadir un flag `is_demo` en `Usuario` y rechazar esas dos rutas, o restringirlas a `admin`/`tecnico` mientras dure la demo. Reseed periódico de la base. |
| SA-008 | MEDIUM | `backend/app/main.py:121-134`, `backend/app/config.py:117-126` | `allow_credentials=True` con orígenes tomados de `CORS_ALLOWED_ORIGINS` sin ninguna validación. Si al desplegar se pone `*` (tentador con las URLs de preview de Vercel), Starlette refleja el `Origin` de la petición cuando hay cookies, habilitando lectura cross-origin autenticada desde cualquier sitio. Hoy el valor por defecto es seguro (`localhost:5173`). | Validar en `Settings` que ningún origen sea `*` ni vacío cuando `APP_ENV` no es desarrollo, y rechazar el arranque. Listar explícitamente el dominio de producción de Vercel. |
| SA-009 | MEDIUM | `.github/workflows/deploy.yml:65-68` | `cp .env.example .env \|\| true` sobre el host de deploy. Verificado que la raíz `.env.example` **no** define `SECRET_KEY` ni `APP_ENV` (sólo `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `COMPOSE_PROJECT_NAME`), y `docker-compose.yml:15,18` resuelve `APP_ENV=production` con `SECRET_KEY` vacío, lo que hace que `config.py:44-51` aborte el arranque. **No hay forja de JWT**: el sistema falla cerrado. El daño real es que MySQL inicializa el volumen con la contraseña root publicada en el repositorio (`.env.example:3`) y el broker MQTT con las credenciales de ejemplo (`.env.example:5-6`); como el volumen ya quedó inicializado, esa contraseña root sigue siendo válida aunque después se cargue un `.env` correcto. El `\|\| true` además oculta el fallo del `cp`. | Sustituir el bloque por un `if [ ! -f .env ]; then echo "FATAL: falta .env"; exit 1; fi`. Nunca materializar un `.env` a partir de la plantilla en un host de despliegue. |
| SA-010 | MEDIUM | `backend/app/middleware/rate_limit.py:64-97` | Sin Redis, `_resolve_storage_uri` cae a `memory://` con sólo un `logger.warning`. En Render free-tier la instancia hiberna tras inactividad, así que los contadores se reinician en cada arranque en frío, y con más de un worker cada proceso lleva su propio contador. Aceptable para un demo de bajo tráfico **sólo** si SA-003 se corrige; combinados, no queda protección real de fuerza bruta. | Aceptar `memory://` para el demo pero documentarlo, y corregir SA-003. Si más adelante hay Redis gratuito (Upstash), apuntar `REDIS_URL` ahí. |
| SA-011 | LOW | `backend/app/routers/metrics.py:240,252` | `/metrics/health-detailed` devuelve `str(exc)` de `SQLAlchemyError` y de errores de Redis al cliente. Los mensajes de SQLAlchemy suelen incluir host, puerto, nombre de base y usuario. La ruta exige autenticación (`main.py:220-228`), así que el consumidor sería un usuario autenticado — incluido el demo. | Registrar la excepción en el log y devolver un mensaje genérico (`"unhealthy"`) al cliente. |
| SA-012 | LOW | `backend/app/routers/auth.py:74`, `backend/app/services/auth_service.py:122` | El login devuelve el `access_token` también en el cuerpo, además de la cookie `HttpOnly`. El frontend no lo persiste (`frontend/src/api/client.js` no lo toca; `LoginPage.jsx:44` sólo comprueba su presencia), pero el token queda expuesto a logs de proxy y a las devtools. | Devolver sólo `{"token_type": "bearer"}` cuando la autenticación sea por cookie, o mantener el cuerpo únicamente para el flujo de API keys/CLI. |
| SA-013 | LOW | `backend/requirements.txt:8` | `python-jose[cryptography]==3.3.0` arrastra CVE-2024-33663 (confusión de algoritmo) y CVE-2024-33664 (DoS al descifrar JWE). **No explotables en este código**: `dependencies.py:83-87` y `auth.py:95-100` fijan `algorithms=["HS256"]` y en ningún punto se llama a `jwe.decrypt`. Se reporta por higiene de dependencias, no como vía de ataque. | Planificar la migración a `pyjwt`, que es la dependencia mantenida y la que la documentación de FastAPI recomienda hoy. Sin urgencia. |
| SA-014 | LOW | `backend/app/routers/equipos.py:202-245` | `POST /equipos/auto-register` es público y sólo valida un JWT de provisioning de 1 h (`equipos.py:52-69`). Quien obtenga ese token (se transporta en un QR) puede crear equipos sin límite durante esa hora. Verificado que ese token **no** sirve como token de sesión: carece de `sub`, y `dependencies.py:88-90` lo rechaza. | Incluir la MAC esperada como claim del token de provisioning y validar que coincida, o marcar el token como de un solo uso. |
| SA-015 | LOW | `backend/app/models/usuario.py:55-56`, servicios en `backend/app/services/` | Ningún servicio filtra consultas por `organizacion_id`; `TenantMiddleware` sólo rechaza cuando el cliente envía un `X-Tenant-ID` que no coincide (`dependencies.py:136-142`). El sistema es de facto mono-tenant. No es explotable con una sola organización, pero el aislamiento por tenant no existe pese a que el modelo lo sugiere. | Para el demo, sin acción. Si se añade una segunda organización, filtrar por `organizacion_id` en cada servicio antes de exponerlo. |

## Rutas de ataque más probables

1. **Toma de control total en dos peticiones** (SA-001): `POST /auth/register` con `{"rol":"admin", ...}` → `POST /auth/login` → acceso a `/usuarios`, `/api-keys` y `/audit-logs`, incluyendo la creación de API keys IoT y el borrado de la traza de auditoría (`usuarios.py:279` elimina audit logs). Requiere cero conocimiento previo y ninguna de las demás defensas lo detiene.
2. **Fuerza bruta sobre la cuenta demo y sobre el admin sembrado** (SA-003 + SA-010 + `scripts/seed_db.py:178,213`): rotar `X-Forwarded-For` evade el límite de 10/min; los defaults `Admin123!` / `Tecnico123!` con los correos `admin@manttoai.local` y `tecnico@manttoai.local` están publicados en el repositorio y referenciados en `docs/manual-usuario.md:29`, así que ni siquiera hace falta fuerza bruta si la base se sembró con los valores por defecto.
3. **Persistencia mediante credenciales embebidas** (SA-004 + SA-006): si en algún momento se ejecuta `backend/create_admin.py` contra la base desplegada, queda `admin@mantto.ai / admin123` de forma permanente y pública; sin Redis, revocar la sesión resultante no invalida el token durante 4 h.

## Contrato de resultado

- **status**: `findings`
- **executive_summary**: 1 CRITICAL, 3 HIGH, 6 MEDIUM y 5 LOW; el despliegue público no es seguro hasta cerrar SA-001 a SA-004.
- **next_recommended**: `fix-then-reaudit`
- **risks (BLOCKER/CRITICAL sin resolver)**: SA-001 (escalada de privilegios a `admin` desde un registro anónimo).
