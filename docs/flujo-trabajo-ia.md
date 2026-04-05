# Flujo de trabajo del equipo con IA

Este flujo busca **reducir ruido**. La idea no es meter más proceso, sino evitar prompts vagos, cambios gigantes y PRs imposibles de revisar.

## Regla base

**1 issue = 1 branch = 1 PR = 1 objetivo claro**

Si una tarea tiene dos objetivos distintos, se divide.

---

## Flujo recomendado

### 1. Crear la issue

Cada issue debería responder estas 5 cosas:

1. **Qué problema resuelve**
2. **Qué alcance tiene**
3. **Qué queda fuera**
4. **Cómo se valida**
5. **Qué módulo toca**

### 2. Abrir branch desde `develop`

Usar ramas chicas y descriptivas:

- `feature/equipos-crud`
- `feature/dashboard-summary`
- `fix/auth-login-validation`
- `fix/frontend-api-base-url`

### 3. Pedirle trabajo a la IA

Siempre darle contexto mínimo, no un prompt genérico.

#### Prompt base recomendado

```text
Implementá la issue <ID> de ManttoAI.

Antes de cambiar código:
- leé AGENTS.md
- leé docs/arquitectura-manttoai.md
- leé docs/flujo-trabajo-ia.md
- leé esta issue completa

Restricciones:
- no inventar arquitectura nueva
- mantener cambios chicos
- comentarios en español
- no salir del scope de la issue

Objetivo:
<pegar objetivo de la issue>

Criterios de aceptación:
<pegar acceptance criteria>

Verificación requerida:
<pegar comandos o checks esperados>
```

#### Buenos prompts

- “Implementá la issue #12: guardar lecturas MQTT en DB y exponer historial.”
- “Resolvé la issue #18 respetando router → service → model. No mezcles lógica en routers.”

#### Malos prompts

- “hacé el backend”
- “seguí con el proyecto”
- “mejorá todo”

---

## Cómo escribir una buena issue

### Título

Usar verbo + resultado:

- `Implement dashboard summary endpoint`
- `Add telemetry simulator for MQTT`
- `Fix login validation response`

### Cuerpo mínimo

```md
## Objetivo
Qué hay que lograr.

## Contexto
Qué parte del sistema toca y por qué importa.

## Alcance
- En scope:
- Fuera de scope:

## Criterios de aceptación
- [ ] criterio 1
- [ ] criterio 2
- [ ] criterio 3

## Verificación sugerida
- comando 1
- comando 2

## Módulos afectados
- Backend / Frontend / IoT / ML / Infra
```

---

## Verificación antes de abrir PR

### Si tocaste backend

```bash
make lint
make test
```

### Si tocaste frontend

```bash
make lint-front
make build-front
```

Si Playwright ya está configurado para esa tarea:

```bash
make e2e-front
```

> Si Playwright falla por navegador faltante, corré una vez:

```bash
cd frontend && npx playwright install chromium
```

### Si tocaste Docker / scripts / compose

```bash
docker compose config --quiet
```

### Si tocaste MQTT / simulador

```bash
make simulate
make mqtt-test
```

---

## Definition of done del equipo

Una tarea se considera terminada cuando:

- la issue quedó cubierta
- el cambio respeta `AGENTS.md`
- la arquitectura no se rompió
- el scope no se desbordó
- la verificación local pasó
- el PR explica cambio, riesgo y validación

---

## Qué evitar

- una branch con varias features mezcladas
- prompts tipo “hacé todo”
- mover archivos de carpeta porque sí
- meter lógica de negocio en routers o componentes grandes
- abrir PR sin correr comandos locales

---

## Recomendación práctica para este proyecto

Para ManttoAI conviene trabajar así:

1. issue chica
2. branch chica
3. IA con prompt acotado
4. verificación local
5. PR chico
6. review
7. merge

Ese flujo baja muchísimo el ruido en proyectos vibe-codeados.
