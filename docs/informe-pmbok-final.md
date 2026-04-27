# Informe Final PMBOK — ManttoAI Predictivo

**Institución:** INACAP  
**Curso:** Gestión de Proyectos Informáticos  
**Fecha de cierre:** 07 de abril de 2026  
**Versión del sistema:** v1.0.0  
**Equipo:**
- Sebastián Bravo (Backend, MQTT/IoT, CI/CD, Deployment)
- Luis Loyola (Frontend, Base de datos, Integración API, Documentación de alcance)
- Ángel Rubilar (Arquitectura, Hardware ESP32, Modelo ML)

---

## 1. Resumen Ejecutivo

**ManttoAI Predictivo** es un prototipo académico de sistema de mantenimiento predictivo que captura telemetría en tiempo real desde dispositivos IoT (ESP32), evalúa riesgos de falla mediante un modelo de Machine Learning (scikit-learn Random Forest), y presenta alertas operacionales en un dashboard web.

### Objetivos del proyecto (alcanzados)
1. ✅ Capturar lecturas de temperatura, humedad y vibración desde ESP32 vía MQTT
2. ✅ Almacenar telemetría en base de datos relacional (MySQL)
3. ✅ Evaluar umbrales operativos y generar alertas automáticas
4. ✅ Ejecutar predicciones de falla con modelo ML (Random Forest)
5. ✅ Mostrar estado, tendencias, alertas e historial en dashboard web
6. ✅ Desplegar sistema completo en VPS con Docker Compose
7. ✅ Documentar arquitectura, flujos y evidencia de QA para entrega académica

### Resultado final
- Sistema 100% funcional con telemetría en tiempo real
- 200 tests backend automatizados (cobertura: 82% core API)
- 7 tests E2E con Playwright (flujos críticos de usuario)
- Simulador IoT 24/7 integrado para demo continua
- Auto-refresh en todas las páginas del dashboard (10-20s)
- CI/CD con GitHub Actions validando cada PR
- Deployment automático en VPS con Dokploy

---

## 2. Gestión del Alcance

### Alcance planificado original
- Telemetría IoT desde ESP32 (temperatura, humedad, vibración)
- Backend FastAPI con API REST y MQTT subscriber
- Base de datos MySQL
- Modelo ML básico (scikit-learn)
- Frontend React con dashboard y alertas
- Deployment en VPS con Docker

### Alcance entregado (v1.0.0)
- ✅ Telemetría IoT con ESP32 + MQTT (Mosquitto)
- ✅ Backend FastAPI completo (auth, equipos, lecturas, alertas, predicciones, mantenciones, umbrales, dashboard)
- ✅ Base de datos MySQL con migraciones
- ✅ Modelo ML Random Forest con 94.1% accuracy y 93.0% F1-score
- ✅ Frontend React con 7 páginas (Login, Dashboard, Equipos, Equipos Detalle, Alertas, Historial, NotFound)
- ✅ Auto-refresh en todas las páginas críticas (polling inteligente)
- ✅ Simulador IoT 24/7 integrado en backend
- ✅ CI/CD con GitHub Actions (lint, tests, E2E)
- ✅ Deployment automatizado en VPS con Dokploy
- ✅ Documentación técnica completa

### Cambios de alcance aprobados
1. **Simulador IoT 24/7:** Inicialmente era script CLI de ejecución finita. Se integró como servicio continuo en backend para demostración sin intervención manual.
2. **Auto-refresh frontend:** No estaba en alcance inicial. Se agregó por requisito crítico de UX (sistema de monitoreo debe actualizar automáticamente).
3. **Dokploy:** Inicialmente se planeó deployment manual con Docker Compose. Se adoptó Dokploy para GitOps y deployment automático.

### Fuera de alcance (confirmado)
- ❌ Microservicios / Kubernetes / Serverless
- ❌ Deep Learning / TensorFlow / PyTorch
- ❌ Integración con ERP/SCADA/Modbus/OPC-UA
- ❌ Mobile app / PWA
- ❌ LoRa / 4G / otros protocolos IoT
- ❌ Múltiples roles de usuario (solo admin)
- ❌ Notificaciones push/SMS (solo email opcional)

---

## 3. Gestión del Cronograma

### Hitos principales

| Hito | Fecha Planificada | Fecha Real | Estado |
|------|-------------------|------------|--------|
| Definición de arquitectura | 2026-03-15 | 2026-03-14 | ✅ Adelantado |
| Backend API core | 2026-03-25 | 2026-03-23 | ✅ Adelantado |
| Frontend MVP | 2026-03-30 | 2026-04-01 | ⚠️ Retraso menor (2 días) |
| Modelo ML entrenado | 2026-04-02 | 2026-04-02 | ✅ A tiempo |
| Integración MQTT | 2026-04-03 | 2026-04-03 | ✅ A tiempo |
| Tests automatizados | 2026-04-05 | 2026-04-06 | ⚠️ Retraso menor (1 día) |
| Deployment VPS | 2026-04-06 | 2026-04-06 | ✅ A tiempo |
| Code freeze v1.0.0 | 2026-04-07 | 2026-04-07 | ✅ A tiempo |

### Variaciones significativas
- **Frontend MVP:** Se retrasó 2 días por refactorización de componentes para mejorar UX (auto-refresh, estados de loading).
- **Tests automatizados:** Se retrasó 1 día por issue con fixtures de base de datos y aislamiento de tests.

### Lecciones aprendidas (cronograma)
1. **Testing debe iniciar antes:** Los tests se desarrollaron tarde. Idealmente deben escribirse en paralelo con la implementación.
2. **Buffers funcionan:** Se dejó 1 día de buffer antes del code freeze. Fue suficiente para resolver issues finales.
3. **Frontend subestimado:** React + Vite + Tailwind es rápido, pero el pulido de UX consume más tiempo del esperado.

---

## 4. Gestión de Costos

### Presupuesto planificado
- **Hardware ESP32:** USD $60 (3 kits DevKit v1 + sensores DHT22 + MPU-6050)
- **VPS:** USD $20/mes × 2 meses = USD $40
- **Dominio:** USD $0 (se usó IP pública del VPS)
- **Herramientas:** USD $0 (stack open-source)
- **Total planificado:** USD $100

### Costos reales
- **Hardware ESP32:** USD $58 (compra real)
- **VPS:** USD $20/mes × 2 meses = USD $40 (Hetzner CX22)
- **Dominio:** USD $0
- **Herramientas:** USD $0
- **Total real:** USD $98

### Variación de costos
- **USD -$2 (2% ahorro):** Se encontró proveedor local con descuento en kits ESP32.

### ROI académico
- **Inversión:** USD $98
- **Retorno esperado:** Aprobación del curso + portfolio técnico + experiencia en stack moderno
- **ROI no monetario:** Alto (proyecto reutilizable en CV, conocimiento transferible a entorno laboral)

---

## 5. Gestión de Calidad

### Métricas de calidad del código

| Métrica | Meta | Real | Estado |
|---------|------|------|--------|
| Cobertura de tests backend | ≥ 70% | 82% (200 tests) | ✅ |
| Tests E2E frontend | ≥ 5 flujos | 7 flujos | ✅ Superado |
| Lint warnings | 0 | 0 | ✅ |
| Build sin errores | 100% | 100% | ✅ |
| CI/CD verde en PRs | 100% | 98% | ⚠️ (2 PRs con fallas corregidas) |
| Tiempos de respuesta API | < 500ms | < 200ms | ✅ Superado |

### Métricas de calidad del modelo ML

| Métrica | Meta | Real | Estado |
|---------|------|------|--------|
| Accuracy validación | ≥ 80% | 94.1% | ✅ Superado |
| Precision | ≥ 0.75 | 0.94 | ✅ Superado |
| Recall | ≥ 0.75 | 0.92 | ✅ Superado |
| F1-score | ≥ 0.80 | 0.93 | ✅ Superado |

### Pruebas ejecutadas

#### Backend (pytest)
```bash
$ pytest tests/ -v --cov=app
200 passed, 2 skipped in 16.05s
Coverage: 82% (core API)
```

**Cobertura por módulo:**
- ✅ Auth: 100%
- ✅ Equipos: 95%
- ✅ Lecturas: 90%
- ✅ Alertas: 85%
- ✅ Predicciones: 80%
- ⚠️ MQTT subscriber: 60% (difícil de testear en CI)
- ⚠️ ML scripts: 50% (scripts CLI, no endpoints)

#### Frontend (Playwright E2E)
- ✅ Login exitoso
- ✅ Login fallido (credenciales inválidas)
- ✅ Navegación Dashboard → Equipos → Alertas → Historial
- ✅ Visualización de equipos con datos
- ✅ Detalle de equipo con lecturas y predicciones
- ✅ Alertas activas visibles
- ✅ Logout exitoso

#### Validación funcional end-to-end
- ✅ Lectura desde simulador → MQTT → Backend → MySQL → Frontend (verificado manualmente)
- ✅ Generación de alerta por umbral excedido (verificado con `qa-mqtt-live-test-prediction-updated.png`)
- ✅ Ejecución de predicción ML y visualización en dashboard (verificado con `qa-equipo-detalle-prediccion-ml.png`)

### Incidencias de calidad encontradas y resueltas

| ID | Descripción | Severidad | Estado | Resolución |
|----|-------------|-----------|--------|------------|
| QA-001 | Tests fallando por fixtures compartidas | Media | ✅ Resuelto | Refactorizar fixtures con scope=function |
| QA-002 | Frontend no actualiza sin refresh manual | Alta | ✅ Resuelto | Implementar auto-refresh con usePolling |
| QA-003 | Modelo ML con accuracy < 80% en primera versión | Alta | ✅ Resuelto | Ajustar hiperparámetros y feature engineering |
| QA-004 | MQTT subscriber no corría 24/7 | Media | ✅ Resuelto | Integrar simulador como servicio en backend |
| QA-005 | CI con warnings de linter | Baja | ✅ Resuelto | Corregir imports y dependencias React hooks |

### Auditoría de código (AI-assisted)
- Se ejecutaron 3 revisiones de código con agente `code-reviewer` sobre módulos críticos (auth, alertas, predicciones)
- **Resultado:** 0 issues de severidad crítica, 2 recomendaciones menores aplicadas

---

## 6. Gestión de Riesgos

### Riesgos identificados y mitigados

| ID | Riesgo | Probabilidad | Impacto | Estrategia | Estado Final |
|----|--------|--------------|---------|------------|--------------|
| R01 | Inestabilidad Wi-Fi en ESP32 | Alta | Alto | Implementar simulador MQTT backend 24/7 | ✅ Mitigado |
| R02 | Modelo ML con Accuracy < 80% | Media | Alto | Tuning de hiperparámetros y dataset sintético | ✅ Cerrado (Acc=94.1%) |
| R03 | Retraso importación sensores | Media | Medio | Comprar stock local (MercadoLibre) | ✅ Cerrado |
| R04 | Frontend desactualizado (Stale Data) | Baja | Alto | Implementar auto-refresh/polling en React | ✅ Mitigado |
| R05 | Caída VPS durante Demo | Baja | Alto | Script local de Docker Compose de respaldo | Activo |
| R06 | Falla de Integración Continua (CI) | Media | Medio | Tests automatizados y linting estricto | Activo |
| R07 | Sobrepaso de presupuesto | Baja | Medio | Uso exclusivo de Open-Source y VPS económico | ✅ Cerrado |

*Nota: El registro formal detallado con puntajes de la matriz P/I se encuentra en [docs/riesgos/24-registro-riesgos.md](../riesgos/24-registro-riesgos.md).*

### Riesgos residuales
- **R-RES-01:** MQTT sin TLS (se acepta para prototipo académico, no para producción)
- **R-RES-02:** Un solo usuario admin (no hay roles diferenciados)
- **R-RES-03:** Modelo ML no reentrenable desde UI (requiere acceso a servidor)

---

## 7. Gestión de Recursos Humanos

### Equipo y roles

| Integrante | Rol Principal | Contribución Real | Desempeño |
|------------|---------------|-------------------|-----------|
| Sebastián Bravo | Backend + DevOps | 40% del código total, CI/CD, deployment, MQTT | ⭐⭐⭐⭐⭐ |
| Luis Loyola | Frontend + DB | 35% del código total, React, schemas MySQL | ⭐⭐⭐⭐⭐ |
| Ángel Rubilar | Arquitectura + ML | 25% del código total, diseño, modelo ML, ESP32 | ⭐⭐⭐⭐⭐ |

### Dinámica de trabajo
- **Metodología:** PMBOK con adaptaciones ágiles (sprints semanales informales)
- **Comunicación:** Discord diario + reunión semanal presencial
- **Control de versiones:** Git + GitHub con PRs obligatorias
- **Documentación:** Markdown en repo, actualizada en tiempo real

### Lecciones aprendidas (equipo)
1. ✅ **Pair programming funciona:** Sesiones de pair en issues críticas aceleraron resolución.
2. ✅ **AI-assisted dev acelera:** Uso de agentes IA redujo tiempo de boilerplate en ~30%.
3. ⚠️ **Más tests desde día 1:** Testing debería ser paralelo a desarrollo, no secuencial.

---

## 8. Gestión de Comunicaciones

### Stakeholders

| Stakeholder | Rol | Interés | Comunicación |
|-------------|-----|---------|--------------|
| Profesor del curso | Evaluador | Aprobación académica | Presentación final + informe PMBOK |
| Equipo de desarrollo | Implementadores | Aprendizaje técnico | Discord + GitHub |
| Usuario final (ficticio) | Operador industrial | Monitoreo de equipos | Manual de usuario + video demo |

### Artefactos de comunicación entregados
- ✅ README.md técnico
- ✅ docs/manual-usuario.md
- ✅ docs/demo.md (script de demostración)
- ✅ docs/arquitectura-manttoai.md
- ✅ docs/informe-pmbok-final.md (este documento)
- ✅ Presentación final (preparada para defensa)
- ⏳ Video de demo (pendiente de grabación)

---

## 9. Gestión de Adquisiciones

### Adquisiciones realizadas

| Ítem | Proveedor | Costo | Fecha | Estado |
|------|-----------|-------|-------|--------|
| 3× ESP32 DevKit v1 | MercadoLibre CL | USD $30 | 2026-03-10 | ✅ Entregado |
| 3× DHT22 | MercadoLibre CL | USD $18 | 2026-03-10 | ✅ Entregado |
| 3× MPU-6050 | MercadoLibre CL | USD $10 | 2026-03-10 | ✅ Entregado |
| VPS Hetzner CX22 | Hetzner Cloud | USD $20/mes | 2026-03-15 | ✅ Activo |

### Lecciones aprendidas (adquisiciones)
- ✅ Comprar hardware con buffer de tiempo (llegó 2 días antes de lo esperado)
- ✅ VPS más barato (4GB RAM) hubiera sido suficiente

---

## 10. Gestión de Interesados

### Satisfacción de stakeholders

| Stakeholder | Expectativa | Resultado | Satisfacción |
|-------------|-------------|-----------|--------------|
| Profesor | Proyecto funcional alineado a PMBOK | Sistema 100% funcional con docs completas | ⭐⭐⭐⭐⭐ (esperada) |
| Equipo | Aprendizaje técnico + portfolio | Stack moderno, CI/CD, ML, IoT aprendidos | ⭐⭐⭐⭐⭐ |
| Usuario ficticio | Dashboard útil y reactivo | Auto-refresh, alertas en tiempo real | ⭐⭐⭐⭐⭐ |

---

## 11. Cierre del Proyecto

### Criterios de éxito (validados)
- ✅ Sistema desplegado y accesible vía web
- ✅ Telemetría en tiempo real funcionando
- ✅ Modelo ML con accuracy ≥ 80%
- ✅ Dashboard con auto-refresh
- ✅ Tests automatizados (backend + frontend)
- ✅ CI/CD configurado
- ✅ Documentación completa
- ✅ Código limpio y sin debug residual

### Entregables finales
1. ✅ Repositorio GitHub público: [github.com/sebitabravo/ManttoAI](https://github.com/sebitabravo/ManttoAI)
2. ✅ Sistema desplegado en VPS (accesible para demo)
3. ✅ Informe PMBOK (este documento)
4. ✅ Presentación final (preparada para defensa)
5. ⏳ Video de demo (pendiente de grabación)
6. ✅ Manual de usuario (docs/manual-usuario.md)

### Recomendaciones para proyectos futuros
1. **Iniciar testing desde sprint 1:** No dejar tests para el final.
2. **Adoptar TDD en módulos críticos:** Auth y ML deberían hacerse con TDD.
3. **Más tiempo para frontend:** UX consume más de lo estimado.
4. **CI/CD desde día 1:** GitHub Actions configurado temprano evita sorpresas.
5. **Documentar decisiones técnicas:** ADRs (Architecture Decision Records) ayudan a justificar elecciones.

### Lecciones aprendidas generales
1. ✅ **Simplicity wins:** La arquitectura simple (monolito Docker Compose) fue la correcta para MVP.
2. ✅ **AI-assisted development es real:** Agentes IA aceleraron desarrollo sin comprometer calidad.
3. ✅ **Polling > WebSockets para MVP:** Auto-refresh con polling fue más simple y suficiente.
4. ⚠️ **Tests requieren disciplina:** No es automático, hay que forzar la práctica.

---

## 12. Referencias

- [Repositorio GitHub](https://github.com/sebitabravo/ManttoAI)
- [Documentación técnica](https://github.com/sebitabravo/ManttoAI/tree/main/docs)
- [Guía PMBOK 6ta edición](https://www.pmi.org/pmbok-guide-standards)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React 18 Docs](https://react.dev/)
- [scikit-learn Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Mosquitto MQTT](https://mosquitto.org/)
- [Docker Compose](https://docs.docker.com/compose/)

---

**Fecha de cierre formal:** 07 de abril de 2026  
**Versión del documento:** 1.0  
**Aprobado por:** Equipo ManttoAI (Sebastián Bravo, Luis Loyola, Ángel Rubilar)
