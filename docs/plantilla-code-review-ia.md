# Plantilla estándar para Code Review con IA

Esta guía estandariza cómo pedir y publicar revisiones de código asistidas por IA (Claude, Gemini, etc.) para que el output sea **consistente, comparable y accionable**.

## Objetivo

- Mantener el mismo formato de review en todos los PR.
- Reducir comentarios vagos o sin evidencia.
- Separar observaciones críticas de sugerencias menores.

---

## 1) Prompt maestro (entrada para cualquier IA)

Copiar y pegar este bloque al pedir una review:

```text
Actuá como revisor técnico senior del repositorio ManttoAI.

Contexto del proyecto:
- Proyecto académico MVP (simplicidad > complejidad enterprise)
- Stack principal: FastAPI + MySQL + React + MQTT
- Restricciones: no inventar arquitectura nueva, no salir del alcance del PR

Alcance de revisión:
- PR: <numero-o-url>
- Rama base: <base-branch>
- Revisar TODOS los commits y el diff completo (no solo el último commit)

Reglas obligatorias:
1) No inventar hallazgos.
2) Cada hallazgo debe incluir severidad, archivo:línea y evidencia técnica.
3) Si algo no se puede confirmar, marcarlo como "No verificado".
4) Priorizar seguridad, correctitud y riesgo de producción.
5) No bloquear por estilo menor o preferencias personales.
6) Si hay hallazgos Critical/High sin resolver, el veredicto NO puede ser APPROVE.

Categorías de severidad:
- Critical: riesgo de seguridad, pérdida de datos, caída del sistema.
- High: bug funcional importante o riesgo alto de regresión.
- Medium: deuda técnica o bug acotado sin impacto crítico inmediato.
- Low: mejora menor o recomendación de mantenimiento.

Formato de salida obligatorio:
1) Resumen ejecutivo (máximo 3 bullets)
2) Tabla de hallazgos
3) Checklist de revisión
4) Riesgos residuales
5) Veredicto final: APPROVE / REQUEST_CHANGES / BLOCK

No agregues secciones fuera de este formato.
```

---

## 2) Formato obligatorio de salida (lo que debe publicar la IA)

```markdown
## Code Review IA — ManttoAI

### 1) Resumen ejecutivo
- ...
- ...
- ...

### 2) Hallazgos
| ID | Severidad | Tipo | Archivo:Línea | Hallazgo | Evidencia | Recomendación |
|---|---|---|---|---|---|---|
| H-01 | High | Correctitud | backend/app/...:123 | ... | ... | ... |

### 3) Checklist
- Correctitud funcional: ✅ / ⚠️ / ❌
- Seguridad (auth, secrets, validación): ✅ / ⚠️ / ❌
- Performance básica: ✅ / ⚠️ / ❌
- Tests y validación: ✅ / ⚠️ / ❌
- Documentación / contratos (API, MQTT): ✅ / ⚠️ / ❌

### 4) Riesgos residuales
- ...

### 5) Veredicto
**APPROVE / REQUEST_CHANGES / BLOCK**

### 6) Alcance y confianza
- Cobertura de revisión: completa / parcial
- Limitaciones: ...
```

> Nota: Si la IA no puede obtener `archivo:línea`, debe indicarlo explícitamente como **No verificado** y no presentar afirmaciones categóricas.

---

## 3) Reglas de decisión del veredicto

- **APPROVE**: sin hallazgos Critical/High pendientes.
- **REQUEST_CHANGES**: hay hallazgos Medium/High corregibles antes de merge.
- **BLOCK**: existe al menos 1 hallazgo Critical o riesgo severo no mitigado.

---

## 4) Publicar la review en GitHub

Para dejar el comentario final estandarizado:

```bash
cp .github/AI_REVIEW_COMMENT_TEMPLATE.md /tmp/review-pr.md
# completar /tmp/review-pr.md con los hallazgos reales
gh pr comment <numero-pr> --body-file /tmp/review-pr.md
```

Si se completa manualmente, usar el mismo formato y secciones.

---

## 5) No negociables para ManttoAI

- No exponer secretos, credenciales ni `.env`.
- No aprobar cambios que rompan flujo MQTT → backend → alertas/predicción.
- No sugerir sobre-ingeniería fuera del alcance académico.
- Priorizar cambios pequeños y verificables.
