# ✅ Checklist de Defensa - ManttoAI v1.0.0

> **Proyecto**: Sistema de Mantenimiento Predictivo con IoT y Machine Learning  
> **Institución**: INACAP  
> **Equipo**: Sebastián Bravo, Luis Loyola, Ángel Rubilar  
> **Fecha límite defensa**: Por definir  
> **Versión**: 1.0.0 (Production Ready)

---

## 📋 Pre-defensa (24 horas antes)

### Infraestructura

- [ ] VPS/servidor accesible desde red INACAP
- [ ] Docker y Docker Compose instalados
- [ ] Ports abiertos: 8000 (backend), 5173/80 (frontend), 3306 (MySQL), 1883 (MQTT)
- [ ] Dominio o IP pública configurada (opcional)
- [ ] SSL/TLS certificado instalado (opcional, pero recomendado)

### Código y Repositorio

- [ ] Repositorio GitHub público con README actualizado
- [ ] Último commit pusheado a `main`
- [ ] Tags de versión creados: `v1.0.0`
- [ ] GitHub Actions passing (si están configurados)
- [ ] Sin archivos `.env` commiteados (validar .gitignore)

### Documentación

- [ ] `README.md` actualizado con instrucciones de instalación
- [ ] `docs/arquitectura-manttoai.md` completo
- [ ] `docs/api-endpoints.md` con ejemplos de requests
- [ ] `docs/modelo-ml.md` con métricas del modelo
- [ ] `docs/manual-usuario.md` con capturas de pantalla
- [ ] `docs/informe-pmbok-final.md` listo para entregar
- [ ] `docs/presentacion-final.md` revisado y practicado
- [ ] ADRs documentados en `docs/decisiones/`

### Stack y Servicios

- [ ] `docker compose up -d` ejecutado sin errores
- [ ] 4 servicios HEALTHY: backend, frontend, mysql, mosquitto
- [ ] Backend responde en `/health` con status "ok"
- [ ] Frontend accesible en navegador
- [ ] Base de datos poblada con datos demo (`seed_db.py`)
- [ ] Simulador IoT generando lecturas cada 30s

### Tests y Calidad

- [ ] `pytest` passing con >= 75% cobertura
- [ ] `ruff check .` sin errores críticos
- [ ] `black --check .` formateado correcto
- [ ] ESLint sin warnings en frontend
- [ ] Frontend build sin errores: `npm run build`

### Machine Learning

- [ ] Modelo `modelo.joblib` presente en `backend/app/ml/`
- [ ] Dataset `synthetic_readings.csv` con >= 1000 filas
- [ ] `evaluate.py` ejecutado con métricas >= 80% F1
- [ ] Feature importance documentado
- [ ] Cross-validation ejecutado (5-fold)

### Demo Preparada

- [ ] Script `demo-defensa.sh` probado de principio a fin
- [ ] Video de demo grabado (backup en caso de problemas técnicos)
- [ ] Capturas de pantalla del dashboard guardadas
- [ ] Ejemplo de CURL requests documentado
- [ ] Navegador con tabs pre-abiertos: dashboard, GitHub, docs

---

## 🎤 Durante la defensa (checklist de presentación)

### Introducción (3-5 min)

- [ ] Presentación del equipo y roles
- [ ] Contexto del problema: mantenimiento reactivo vs predictivo
- [ ] Objetivo del proyecto y alcance académico
- [ ] Stack tecnológico overview

### Demo técnica (10-15 min)

**Opción A: Script automatizado**
- [ ] Ejecutar `./scripts/demo-defensa.sh` paso a paso
- [ ] Explicar cada paso mientras se ejecuta
- [ ] Mostrar outputs clave (health check, JWT, dashboard, ML)

**Opción B: Demo manual**
- [ ] Mostrar `docker compose ps` - todos servicios HEALTHY
- [ ] Abrir dashboard en navegador
- [ ] Login con usuario demo
- [ ] Mostrar equipos monitoreados con temperaturas en tiempo real
- [ ] Mostrar alertas activas
- [ ] Ejecutar predicción de riesgo para un equipo
- [ ] Mostrar gráficos de tendencias
- [ ] Publicar lectura simulada vía MQTT
- [ ] Verificar que aparece en dashboard (auto-refresh)

### Arquitectura (5-7 min)

- [ ] Mostrar diagrama de arquitectura (docs o slides)
- [ ] Explicar flujo de datos: ESP32 → MQTT → Backend → DB → Frontend
- [ ] Justificar elección de tecnologías (ADRs)
- [ ] Explicar separación de capas (IoT, Backend, ML, Frontend)
- [ ] Mencionar escalabilidad y extensibilidad

### Machine Learning (5-7 min)

- [ ] Mostrar output de `evaluate.py` con métricas
- [ ] Explicar features usadas: temperatura, humedad, vibración
- [ ] Justificar Random Forest vs otros modelos (ADR-002)
- [ ] Mostrar feature importance
- [ ] Explicar threshold de riesgo (ej: prob >= 0.75)
- [ ] Mencionar validación cruzada (K-Fold)

### Metodología PMBOK (5 min)

- [ ] Mostrar informe PMBOK final
- [ ] Explicar áreas de conocimiento aplicadas:
  - Alcance: WBS, requisitos funcionales
  - Cronograma: Gantt, hitos cumplidos
  - Costos: presupuesto low-cost
  - Calidad: tests, code review, métricas ML
  - Recursos: equipo de 3 personas
  - Comunicación: GitHub, docs, ADRs
  - Riesgos: identificados y mitigados
  - Adquisiciones: hardware ESP32, servicios cloud

### Resultados y Métricas (3 min)

- [ ] Métricas ML: Accuracy 81%, F1 80%, Precision 82%, Recall 78%
- [ ] Cobertura de tests: 78%
- [ ] Uptime del sistema: 99%+ (demo)
- [ ] Tiempo de respuesta API: < 200ms
- [ ] Costo total hardware: ~$30 USD por equipo
- [ ] Costo total proyecto: ~$50 USD (VPS + dominio)

### Lecciones Aprendidas (2-3 min)

- [ ] Desafíos técnicos enfrentados:
  - Integración MQTT con backend
  - Generación de dataset sintético realista
  - Tuning del modelo ML para alcanzar 80% F1
  - Design system del frontend
- [ ] Decisiones arquitectónicas clave (ADRs)
- [ ] Trade-offs aceptados (simplicidad vs features enterprise)

### Trabajo Futuro (2 min)

- [ ] Hardware ESP32 real en campo (actualmente simulado)
- [ ] Más algoritmos ML (XGBoost, Prophet para series temporales)
- [ ] Alertas vía WhatsApp/Telegram (además de email)
- [ ] Dashboard mobile (React Native)
- [ ] Integración con ERP/CMMS externo
- [ ] Multi-tenancy para múltiples empresas

### Preguntas Frecuentes (preparadas)

**P: ¿Por qué MQTT en lugar de HTTP directo?**
- [ ] R: Protocolo ligero, ideal para IoT. Reconexión automática, pub-sub pattern, menor consumo de batería. Ver ADR-001.

**P: ¿Por qué Random Forest y no deep learning?**
- [ ] R: Dataset pequeño (1200 registros), modelo interpretable (feature importance), no requiere GPU, alcanza objetivo de 80% F1. Ver ADR-002.

**P: ¿Cómo validaron el modelo ML sin datos reales?**
- [ ] R: Dataset sintético con distribuciones realistas, validación cruzada 5-fold, métricas conservadoras. En producción se reentrenarÍa con datos reales.

**P: ¿El sistema es escalable?**
- [ ] R: Arquitectura modular, Docker Compose permite migrar a Kubernetes si crece, MySQL soporta millones de lecturas, MQTT broker puede manejar miles de dispositivos.

**P: ¿Cuánto cuesta implementar esto en una empresa real?**
- [ ] R: Hardware ~$30 USD/equipo, VPS básico ~$10 USD/mes, sin licencias. Total < $100 USD inicial para 3 equipos.

**P: ¿Cómo se actualiza el modelo ML?**
- [ ] R: Entrenar offline con nuevos datos, serializar con joblib, reemplazar archivo .joblib en backend, reiniciar servicio. Sin downtime si se usa blue-green deployment.

**P: ¿Qué pasa si el ESP32 pierde conexión WiFi?**
- [ ] R: PubSubClient maneja reconexiones automáticas. Opcionalmente se podría implementar buffer local en SD card para persistir lecturas no enviadas.

**P: ¿Cómo se protege el acceso al sistema?**
- [ ] R: JWT auth con bcrypt, tokens con expiración, HTTPS en producción, variables de entorno para secrets, no hay credenciales en código.

---

## 🛠️ Comandos Útiles para la Defensa

### Verificación rápida pre-defensa

```bash
# Estado del stack
docker compose ps

# Health check backend
curl http://localhost:8000/health

# Login y obtener JWT
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@manttoai.cl","password":"demo123"}'

# Dashboard resumen
TOKEN="<tu-jwt-token>"
curl http://localhost:8000/dashboard/resumen \
  -H "Authorization: Bearer $TOKEN"
```

### Demo automatizada

```bash
# Ejecutar script completo de demo
./scripts/demo-defensa.sh

# O paso a paso (comentar pause_demo() en el script)
./scripts/demo-defensa.sh | tee demo-output.log
```

### Reiniciar stack si hay problemas

```bash
# Parar todo
docker compose down

# Limpiar volúmenes (CUIDADO: borra datos)
docker compose down -v

# Levantar fresh
docker compose up -d

# Re-poblar datos demo
cd backend
source .venv/bin/activate
python -m app.seed_db
```

### Verificar modelo ML en vivo

```bash
cd backend
source .venv/bin/activate
python -m app.ml.evaluate
```

### Tests rápidos

```bash
# Backend
cd backend && pytest tests/ -v --cov=app --tb=short

# Frontend (lint)
cd frontend && npm run lint
```

### Publicar lectura MQTT manualmente

```bash
mosquitto_pub -h localhost -t "manttoai/equipo/1/lecturas" \
  -m '{"temperatura":60,"humedad":70,"vibracion_x":1.0,"vibracion_y":0.8,"vibracion_z":10.5}'
```

### Ver logs en tiempo real

```bash
# Backend
docker compose logs -f backend

# MQTT broker
docker compose logs -f mosquitto

# Todos
docker compose logs -f
```

---

## 📊 Métricas Clave a Memorizar

### Machine Learning
- **Accuracy**: 81.25% ✅
- **F1-Score**: 80.18% ✅
- **Precision**: 81.98% ✅
- **Recall**: 78.45% ✅
- **Cross-Validation F1**: 72.51% (5-fold)
- **Modelo**: Random Forest Classifier, 100 estimadores
- **Features**: 5 (temperatura, humedad, vib_x, vib_y, vib_z)
- **Dataset**: 1,201 lecturas sintéticas

### Backend
- **Framework**: FastAPI 0.115+
- **Tests**: 105 passed, 2 skipped
- **Cobertura**: 78%
- **Endpoints**: 25+ rutas REST
- **Autenticación**: JWT con expiración 7 días
- **Linters**: ruff + black passing

### Frontend
- **Framework**: React 18 + Vite 6
- **Bundle JS**: 272 kB (84 kB gzip)
- **Build time**: ~2 segundos
- **Componentes**: 20+ componentes reutilizables
- **Páginas**: 8 vistas (Dashboard, Equipos, Alertas, Mantenimientos, etc.)

### IoT
- **Hardware**: ESP32 DevKit v1 (~$10 USD)
- **Sensores**: DHT22 + MPU6050 (~$15 USD)
- **Protocolo**: MQTT sobre Wi-Fi
- **Frecuencia**: Lectura cada 30 segundos
- **Broker**: Mosquitto (open source)

### Infraestructura
- **Servicios**: 4 (backend, frontend, mysql, mosquitto)
- **Estado**: Todos HEALTHY
- **Tiempo de start**: ~15 segundos
- **Uptime demo**: 18+ horas sin caídas
- **Costo mensual**: ~$10 USD VPS básico

### Proyecto
- **Duración**: ~3 meses (Nov 2024 - Ene 2025)
- **Equipo**: 3 personas
- **Commits**: 150+ commits
- **Líneas de código**: ~15,000 (backend + frontend + scripts)
- **Documentación**: 10+ archivos MD, 6 ADRs
- **Costo total**: ~$50 USD (hardware + hosting)

---

## 🎯 Tips para la Defensa

### Preparación mental
- [ ] Practicar presentación 3+ veces
- [ ] Cronometrar cada sección
- [ ] Preparar respuestas a preguntas difíciles
- [ ] Dormir bien la noche anterior

### Durante la presentación
- [ ] Hablar claro y pausado
- [ ] Mirar a todos los evaluadores, no solo a las slides
- [ ] Si algo falla técnicamente, tener video/capturas de backup
- [ ] No mentir si no sabes algo: "Es una excelente pregunta, investigaré eso para implementación futura"
- [ ] Destacar trabajo en equipo y metodología PMBOK

### Errores a evitar
- ❌ Memorizar script palabra por palabra (suena robótico)
- ❌ Leer slides literalmente
- ❌ Exceso de jerga técnica sin explicar
- ❌ Demo sin practicar previamente
- ❌ Olvidar mencionar metodología PMBOK
- ❌ No tener plan B si falla internet/laptop

### Fortalezas a destacar
- ✅ Sistema completo end-to-end funcional
- ✅ ML real con métricas validadas
- ✅ Open source, costo bajísimo
- ✅ Documentación completa (ADRs, arquitectura, API)
- ✅ Tests automatizados con buena cobertura
- ✅ Metodología profesional (Git, CI/CD, Docker)
- ✅ Aplicación real en industria (no solo académico)

---

## 📝 Post-defensa

- [ ] Actualizar README con feedback de evaluadores
- [ ] Publicar video de demo en YouTube (privado o público)
- [ ] Agregar badge "Proyecto de Título INACAP 2025" al README
- [ ] Celebrar 🎉

---

**Última actualización**: 2026-04-07  
**Estado**: ✅ Production Ready para defensa
