# Politica de Desarrollo Seguro

- **Version:** 1.0
- **Fecha:** 2026-06-09
- **Clasificacion:** Uso interno / Confidencial
- **Aprobado por:** Director de Proyecto — ManttoAI
- **Proxima revision:** 2026-09-09 (trimestral)

---

## 1. Proposito

Establecer los requisitos de seguridad que deben cumplirse durante todo el ciclo de vida de desarrollo de software de ManttoAI, minimizando la introduccion de vulnerabilidades y garantizando que el codigo producido sea resistente a ataques.

## 2. Alcance

Esta politica aplica a:

- Todo el codigo fuente del backend (Python/FastAPI)
- Todo el codigo fuente del frontend (React/Vite)
- Scripts de infraestructura y despliegue (Docker, shell scripts)
- Dependencias de terceros (librerias, paquetes, imagenes Docker)
- Firmware de dispositivos ESP32 (C/C++ Arduino)
- Pipeline CI/CD

## 3. Principios de Desarrollo Seguro

1. **Seguridad por disenho** — La seguridad se incorpora desde la fase de disenho, no al final
2. **Defensa en profundidad** — Multiples capas de control (codigo, infraestructura, red)
3. **Validacion en ambos extremos** — Frontend y backend validan toda entrada de usuario
4. **No confiar en ningun input** — Todo input externo es potencialmente malicioso
5. **Minimo privilegio** — El codigo solo tiene los permisos necesarios para funcionar
6. **Fallo seguro** — Ante una excepcion o error, el sistema niega acceso por defecto
7. **Registro y auditoria** — Toda accion sensible debe registrarse

## 4. OWASP Top 10 — Mitigaciones Especificas

### A01:2021 — Broken Access Control

| Riesgo | Mitigacion en ManttoAI | Verificacion |
|---|---|---|
| Escalacion de privilegios | JWT con claims de rol verificados en cada endpoint | Tests de autorizacion por rol |
| Acceso a recursos de otro rubro | Filtro por rubro en queries de datos (visualizador limitado) | Pruebas de aislamiento |
| IDOR (Insecure Direct Object References) | Validacion de pertenencia del recurso al usuario autenticado | Code review |

**Implementacion:**

```python
# Cada endpoint verifica el rol del usuario
@router.get("/equipos/{equipo_id}")
async def get_equipo(equipo_id: int, current_user = Depends(get_current_user)):
    equipo = await equipo_service.get_by_id(equipo_id)

    # visualizador solo ve equipos de su rubro
    if current_user.rol == "visualizador" and equipo.rubro_id != current_user.rubro_id:
        raise HTTPException(status_code=403, detail="Acceso denegado a este rubro")

    return equipo
```

### A02:2021 — Cryptographic Failures

| Riesgo | Mitigacion | Verificacion |
|---|---|---|
| Datos en transito sin cifrar | HTTPS obligatorio (Let's Encrypt + TLS 1.3) | Escaneo SSL |
| Datos en reposo sin cifrar | Cifrado AES-256 en backups; TDE en MySQL (pendiente) | Auditoria de cifrado |
| Uso de algoritmos debiles | Solo AES-256, SHA-256, RSA-2048+ | SAST |

### A03:2021 — Injection

| Riesgo | Mitigacion | Verificacion |
|---|---|---|
| SQL Injection | SQLAlchemy ORM (parametrizacion automatica); consultas raw prohibidas | SAST + code review |
| NoSQL Injection | No aplica (MySQL) | N/A |
| Command Injection | Uso de `subprocess.run` con argumentos, no shell=True | SAST + code review |

**Regla:** No se permiten queries SQL concatenadas. Toda consulta debe usar SQLAlchemy ORM o `text()` con parametros vinculados.

```python
# CORRECTO
result = await db.execute(
    text("SELECT * FROM equipos WHERE rubro_id = :rubro_id"),
    {"rubro_id": rubro_id}
)

# INCORRECTO — prohibido
result = await db.execute(f"SELECT * FROM equipos WHERE rubro_id = {rubro_id}")
```

### A04:2021 — Insecure Design

| Riesgo | Mitigacion |
|---|---|
| Disenho sin threat modeling | Incluir analisis de amenazas en el disenho de cada feature |
| Rate limiting ausente | Limitar peticiones por IP/usuario: 100 req/min por usuario |
| Validacion de datos | Pydantic v2 para validacion de schemas en todos los endpoints |

### A05:2021 — Security Misconfiguration

| Riesgo | Mitigacion |
|---|---|
| Debug habilitado en produccion | `DEBUG=False` en produccion; verificado en CI |
| CORS demasiado permisivo | CORS configurado solo para el dominio del dashboard |
| Headers de seguridad faltantes | Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security |

```python
# app/main.py — Headers de seguridad
@router.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### A06:2021 — Vulnerable and Outdated Components

| Riesgo | Mitigacion | Frecuencia |
|---|---|---|
| Dependencias con CVS conocidas | `pip audit` / `npm audit` en CI | Cada commit |
| Version de Python desactualizada | Python 3.11+; actualizar a 3.12 cuando estable | Anual |
| Imagen Docker base desactualizada | Usar imagenes oficiales con SHA256 pin | Mensual |

### A07:2021 — Identification and Authentication Failures

| Riesgo | Mitigacion |
|---|---|
| Contrasenas debiles | Validacion de complejidad (12+ chars, mayuscula, minuscula, numero, simbolo) |
| Sesiones sin expiracion | JWT con expiracion de 24h; refresh token opcional |
| Fuerza bruta | Bloqueo tras 5 intentos fallidos por 15 minutos |

### A08:2021 — Software and Data Integrity Failures

| Riesgo | Mitigacion |
|---|---|
| Dependencias maliciosas | `npm ci` con lockfile; verificar hash en package-lock.json |
| CI/CD comprometido | Secrets de CI como variables de entorno, no en codigo |
| Actualizaciones sin verificar | Verificar firma de paquetes antes de instalar |

### A09:2021 — Security Logging and Monitoring Failures

| Riesgo | Mitigacion |
|---|---|
| Falta de logging de eventos | Todos los cambios a datos sensibles se loguean |
| Logs sin informacion util | Incluir timestamp, usuario, accion, recurso, resultado |
| Logs accesibles por cualquiera | Solo admin accede a logs de auditoria |

### A10:2021 — Server-Side Request Forgery (SSRF)

| Riesgo | Mitigacion |
|---|---|
| Backend hace requests a URLs arbitrarias | Permitir solo URLs de servicios conocidos |
| Acceso a metadatos internos | Bloquear 169.254.169.254 en Docker |

## 5. Code Review Obligatorio

### 5.1 Reglas

1. **Todo cambio a `main` debe pasar por code review.** Sin excepciones.
2. **El autor del PR no puede aprobar su propio PR.**
3. **Cada PR requiere al menos 1 aprobacion** de un miembro del equipo con conocimiento del area.
4. **El code review verifica**:
   - Correctitud funcional
   - Seguridad (OWASP Top 10)
   - Cumplimiento de la politica de desarrollo seguro
   - Calidad del codigo (legibilidad, mantenibilidad)
   - Cobertura de tests

### 5.2 Checklist de code review

```
[ ] El codigo es legible y esta bien estructurado
[ ] No hay secrets, tokens ni contrasenas hardcodeadas
[ ] Toda entrada de usuario se valida (Pydantic)
[ ] No hay SQL concatenado (solo ORM/queries parametrizadas)
[ ] Los permisos de acceso se verifican en cada endpoint
[ ] No hay dependencias nuevas sin evaluacion de seguridad
[ ] Los tests pasan y cubren el cambio
[ ] No hay debugging statements (print, pdb, etc.)
[ ] Las configuraciones sensibles estan en .env, no en codigo
[ ] Se agregaron logs para eventos importantes
```

### 5.3 Tiempo maximo de revision

| Tipo de cambio | Tiempo maximo para revision |
|---|---|
| Fix critico (bug en produccion) | 2 horas |
| Feature mediana | 24 horas |
| Refactor o cambio menor | 48 horas |

## 6. SAST en CI/CD

### 6.1 Backend (Python)

```yaml
# .github/workflows/sast-backend.yml
name: SAST — Backend
on: [pull_request]

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install bandit
      - run: bandit -r app/ -f json --exit-zero
```

Herramientas: **Bandit** (seguridad Python), **Ruff** (linting general).

### 6.2 Frontend (JavaScript/React)

```yaml
# .github/workflows/sast-frontend.yml
name: SAST — Frontend
on: [pull_request]

jobs:
  eslint-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx eslint . --config .eslintrc-security.js
```

Herramientas: **ESLint** con plugins de seguridad, **npm audit**.

### 6.3 Pipeline CI/CD completo

```yaml
# .github/workflows/ci.yml
name: CI — Seguridad
on: [pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      # ... checkout, setup ...
      - run: ruff check app/            # Lint Python
      - run: npx eslint frontend/src/   # Lint JS/React

  sast:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - run: bandit -r app/             # Seguridad Python

  dependency-scan:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - run: pip-audit                  # Escaneo de dependencias Python
      - run: npm audit --audit-level=high  # Escaneo de dependencias JS

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/ -v --cov=app --cov-fail-under=80
```

## 7. Prohibicion de Secrets en Codigo

### 7.1 Reglas

1. **Ningun secret debe estar en el codigo fuente.** Jamas. En ninguna circunstancia.
2. Las claves API, tokens, contrasenas y certificados se cargan desde variables de entorno.
3. El archivo `.env` esta en `.gitignore` y nunca se commitea.
4. Las variables de entorno en produccion se inyectan via Docker Compose o el orquestador.

### 7.2 Archivos incluidos en .gitignore

```
.env
.env.local
*.key
*.pem
*.cert
secrets/
!secrets/.gitkeep
```

### 7.3 Deteccion de secrets

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan
on: [pull_request]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

Se ejecuta **Gitleaks** en cada PR para detectar secrets accidentalmente commiteados.

### 7.4 Que hacer si se commitea un secret

```
1. ROTACION INMEDIATA: Revocar el secret comprometido
2. REMOCION: git filter-repo o BFG para eliminar del historial
3. ANALISIS: Verificar logs para determinar si el secret fue accedido
4. NOTIFICACION: Informar al Director de Proyecto
```

## 8. Dependency Scanning

### 8.1 Backend (Python)

```bash
# Escaneo de dependencias
pip-audit                    # Escanea vulnerabilidades conocidas
pip list --outdated          # Lista paquetes desactualizados
safety check                 # Escaneo alternativo (base de datos Safety DB)
```

**Frecuencia:** En cada PR (CI) y semanalmente (cron).

**Politica:** Una dependencia con CVE de severidad CRITICAL o HIGH bloquea el merge. Debe actualizarse o mitigarse antes de integrar.

### 8.2 Frontend (JavaScript)

```bash
npm audit --audit-level=high
npx npm-check-updates --interactive  # Revision manual de actualizaciones
```

**Frecuencia:** En cada PR (CI) y semanalmente (cron).

### 8.3 Docker images

```bash
docker scout quick <image>    # Escaneo de imagenes Docker
trivy image <image>           # Escaneo alternativo con Trivy
```

**Frecuencia:** Mensual, o al actualizar imagenes base.

### 8.4 Criterios de aceptacion

| Severidad | Accion |
|---|---|
| **CRITICAL** | Bloquea merge; actualizar o parchear antes de integrar |
| **HIGH** | Bloquea merge; actualizar o parchear antes de integrar |
| **MEDIUM** | No bloquea merge, pero debe planificarse actualizacion en la siguiente iteracion |
| **LOW** | Documentar como deuda tecnica; revisar en proxima actualizacion mayor |

## 9. Gestion de Dependencias

### 9.1 Reglas generales

- Preferir librerias mantenidas activamente (ultima version < 1 ano)
- Verificar reputacion del paquete (descargas, mantenedores, issues) antes de agregar
- No agregar dependencias sin una necesidad clara (principio YAGNI)
- Congelar versiones en `requirements.txt`/`package.json` con version exacta
- Lockfile (`package-lock.json`, `requirements.txt` con hashes) siempre commiteado

### 9.2 Dependencias prohibidas

| Tipo | Ejemplos | Razon |
|---|---|---|
| Paquetes sin mantenimiento | Cualquiera sin commits en > 2 anos | Vulnerabilidades sin parche |
| Paquetes con pocas descargas | < 1000 descargas/semana | Riesgo de typo-squatting o malware |
| Paquetes con CVE no resuelto | Cualquiera con CVE CRITICAL/HIGH activo | Riesgo de explotacion |

## 10. Manejo de Datos Sensibles en Desarrollo

### 10.1 Datos de prueba

- No usar datos reales de clientes en desarrollo ni staging
- Usar datos sinteticos o anonimizados
- Toda telemetria de prueba debe tener un flag `es_prueba = true`

### 10.2 Logging

- No loguear contrasenas, tokens JWT, ni datos personales
- No loguear payloads completos de MQTT (pueden contener identificadores de dispositivo)
- Los logs pueden incluir: usuario (id), accion, recurso, resultado, timestamp

## 11. Capacitacion del Equipo

| Tema | Frecuencia | Responsable |
|---|---|---|
| OWASP Top 10 y mitigaciones | Anual | Backend Lead |
| Uso seguro de Git (no committear secrets) | Al incorporarse | Director de Proyecto |
| Code review de seguridad | Al incorporarse | Backend Lead |
| Manejo de dependencias | Anual | Backend Lead |

## 12. Documentos Relacionados

- [01-politica-seguridad-informacion.md](./01-politica-seguridad-informacion.md) — Politica SGSI
- [02-politica-control-acceso.md](./02-politica-control-acceso.md) — Control de acceso
- [00-gap-assessment.md](./00-gap-assessment.md) — Evaluacion de brecha
- [05-roadmap-certificacion.md](./05-roadmap-certificacion.md) — Roadmap de certificacion

## Control de Cambios

| Version | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-06-09 | Version inicial | Director de Proyecto |

---

> Documento generado en el contexto del proyecto academico ManttoAI — INACAP.
> Proyecto: Plataforma de Monitoreo IoT por Rubro.
