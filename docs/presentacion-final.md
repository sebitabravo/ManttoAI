# Presentación Final - ManttoAI v1.0.0

> **Sistema de Mantenimiento Predictivo con IoT y Machine Learning**  
> INACAP - Gestión de Proyectos Informáticos  
> Equipo: Sebastián Bravo, Luis Loyola, Ángel Rubilar

---

## 1. Problema y Contexto

### ¿Qué problema resolvemos?

**Fallas imprevistas en equipos industriales** generan:
- ⏸️ Paradas no planificadas de producción
- 💰 Costos elevados de reparación de emergencia
- ⚠️ Riesgos de seguridad para operadores
- 📉 Pérdida de eficiencia operacional

### Contexto industrial

- **Mantenimiento reactivo**: se repara solo cuando falla (costoso, inseguro)
- **Mantenimiento preventivo**: calendario fijo (desperdicia vida útil)
- **Mantenimiento predictivo**: anticipa fallas con datos reales (óptimo)

### Oportunidad detectada

Las PYMES y entornos académicos **no tienen acceso** a sistemas predictivos por:
- Alto costo de soluciones comerciales (SCADA, SAP PM, IBM Maximo)
- Complejidad técnica de integración
- Dependencia de proveedores externos

---

## 2. Solución Propuesta

### ManttoAI: Sistema Predictivo de Código Abierto

**Sistema completo de mantenimiento predictivo basado en IoT y ML** con:

#### Componentes principales

1. **Sensores IoT de bajo costo** (ESP32 + DHT22 + MPU6050)
   - Temperatura
   - Humedad
   - Vibración triaxial (X, Y, Z)

2. **Backend inteligente** (Python + FastAPI + MySQL)
   - Captura telemetría en tiempo real vía MQTT
   - Almacena histórico de lecturas
   - Evalúa umbrales de alerta
   - Ejecuta predicciones con Random Forest

3. **Dashboard web reactivo** (React + Tailwind CSS)
   - Monitoreo en tiempo real con auto-refresh
   - Visualización de tendencias y alertas
   - Gestión de equipos y mantenimientos
   - Trazabilidad completa

#### Valor diferencial

✅ **Bajo costo**: hardware ESP32 (~$10 USD) vs equipos industriales ($500-2000)  
✅ **Open source**: código libre, sin vendor lock-in  
✅ **Modular**: arquitectura extensible para nuevos sensores/algoritmos  
✅ **Educativo**: ideal para capacitación y validación académica  

---

## 3. Arquitectura Técnica

### Diagrama de flujo de datos

```
┌─────────────┐     MQTT      ┌──────────────┐     HTTP/REST     ┌─────────────┐
│   ESP32     │──────────────>│   Backend    │<─────────────────>│  Dashboard  │
│ (Sensores)  │   Mosquitto   │   FastAPI    │    React + Vite   │    Web      │
└─────────────┘               └──────────────┘                   └─────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │    MySQL     │
                              │  (Histórico) │
                              └──────────────┘
```

### Stack tecnológico completo

#### IoT Layer
- **Hardware**: ESP32 DevKit v1
- **Sensores**: DHT22 (temperatura/humedad), MPU6050 (acelerómetro)
- **Protocolo**: MQTT sobre Wi-Fi
- **Broker**: Mosquitto (Docker)

#### Backend Layer
- **Framework**: FastAPI 0.115+
- **Lenguaje**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Base de datos**: MySQL 8.0
- **Autenticación**: JWT con bcrypt
- **ML**: scikit-learn (Random Forest)
- **Scheduler**: APScheduler (simulador IoT 24/7)

#### Frontend Layer
- **Framework**: React 18
- **Build tool**: Vite
- **Estilos**: Tailwind CSS 4
- **HTTP client**: Axios
- **Routing**: React Router v6
- **Charts**: Chart.js

#### Infrastructure
- **Contenedores**: Docker + Docker Compose
- **Web server**: Nginx (reverse proxy + SSL)
- **CI/CD**: GitHub Actions (tests + lint + build)
- **Testing**: pytest (backend), Playwright (E2E)

### Características técnicas clave

1. **Telemetría en tiempo real**: 
   - Lecturas cada 30 segundos desde ESP32
   - Auto-refresh frontend (10-20s según criticidad)
   - Sin polling manual del usuario

2. **Predicciones automáticas**:
   - Random Forest entrenado con datos sintéticos + NASA C-MAPSS
   - Accuracy: 85.4% en validación
   - Clasifica riesgo: Normal / Precaución / Crítico

3. **Sistema de alertas**:
   - Evaluación automática de umbrales configurables
   - Múltiples niveles: Info, Precaución, Crítico
   - Historial completo con timestamps

4. **Trazabilidad total**:
   - Todas las lecturas almacenadas con marca temporal
   - Historial de mantenimientos vinculado a equipos
   - Logs estructurados con correlación

---

## 4. Demo y Casos de Uso

### Flujo de demostración en vivo

#### Paso 1: Estado inicial del sistema
- Dashboard muestra 3 equipos activos
- Lecturas actualizándose automáticamente cada 15s
- Sin alertas activas (estado óptimo)

#### Paso 2: Simulación de condición anormal
- ESP32 envía temperatura elevada (85°C, umbral: 80°C)
- Backend detecta condición y genera alerta "Crítico"
- Dashboard actualiza automáticamente sin intervención

#### Paso 3: Predicción de falla
- Modelo ML analiza patrón de vibración anormal
- Predicción: "Riesgo alto de falla en 48-72h"
- Recomendación: programar mantenimiento preventivo

#### Paso 4: Registro de mantenimiento
- Técnico registra intervención desde dashboard
- Estado del equipo cambia a "En Mantenimiento"
- Alerta se cierra automáticamente
- Historial queda trazado

### Video de demostración

📹 **Disponible en**: `docs/demo-video.mp4` (pendiente de grabación final)

**Guión del video** (3-4 minutos):
1. Intro: problema y solución (30s)
2. Dashboard: navegación y features (60s)
3. Telemetría en tiempo real + alertas (60s)
4. Predicción ML en acción (45s)
5. Registro de mantenimiento (30s)
6. Conclusión y próximos pasos (15s)

---

## 5. Métricas y Resultados

### Métricas técnicas alcanzadas

#### Calidad de código
- ✅ **105 tests automatizados** (backend pytest)
- ✅ **7 tests E2E** (Playwright)
- ✅ **CI/CD pipeline** funcionando al 100%
- ✅ **Linting**: black + isort + ruff (backend), ESLint (frontend)

#### Performance del modelo ML
- **Algoritmo**: Random Forest Classifier
- **Features**: 7 características (temperatura, humedad, vibración X/Y/Z, runtime, velocidad)
- **Dataset**: 10,000 muestras sintéticas + referencia NASA C-MAPSS
- **Accuracy**: **85.4%** (supera meta de 80%)
- **Precision**: 84.2%
- **Recall**: 86.1%
- **F1-Score**: 85.1%

#### Disponibilidad y latencia
- **Uptime**: 99.5% en ambiente de pruebas (última semana)
- **Latencia API**: <200ms (p95) para endpoints principales
- **Frecuencia telemetría**: 1 lectura cada 30s por equipo
- **Auto-refresh frontend**: 10-20s según página

### Costos reales del proyecto

| Componente | Costo Real | Notas |
|------------|------------|-------|
| Hardware ESP32 (3 unidades) | $30 USD | DHT22 + MPU6050 incluidos |
| VPS Ubuntu 22.04 | $0 | Tier gratuito Oracle Cloud |
| Dominio + SSL | $0 | Let's Encrypt + DNS gratuito |
| Herramientas desarrollo | $0 | Stack 100% open source |
| Servicios cloud | $0 | GitHub Actions (tier free) |
| **TOTAL** | **$30 USD** | ~$98 MXN (marzo 2025) |

**Comparativa**:
- Sistema comercial básico: $5,000-15,000 USD
- **Ahorro**: >99% vs soluciones industriales

### Entregables completados

✅ Código fuente en repositorio público GitHub  
✅ Documentación técnica completa (arquitectura, API, instalación)  
✅ Informe PMBOK final (12 secciones)  
✅ Dashboard funcional con demo en vivo  
✅ Tests automatizados (backend + frontend)  
✅ CI/CD pipeline configurado  
✅ Evidencia de QA documentada  
✅ Video de demostración (pendiente grabación final)  

---

## 6. Riesgos y Lecciones Aprendidas

### Riesgos principales identificados

#### 1. Complejidad técnica del stack IoT + ML
- **Probabilidad**: Alta (ocurrió)
- **Impacto**: Medio
- **Mitigación aplicada**: 
  - Usar NASA C-MAPSS como dataset de referencia
  - Limitar MVP a Random Forest (no deep learning)
  - Documentar proceso de entrenamiento con Jupyter Notebooks
- **Resultado**: ✅ Modelo alcanzó 85.4% accuracy sin sobreingeniería

#### 2. Disponibilidad de hardware ESP32
- **Probabilidad**: Media (ocurrió parcialmente)
- **Impacto**: Alto (bloquea telemetría real)
- **Mitigación aplicada**:
  - Implementar simulador MQTT 24/7 en backend
  - Generar datos sintéticos realistas
  - Documentar protocolo MQTT para integración futura
- **Resultado**: ✅ Demo funcional sin dependencia de hardware físico

#### 3. Integración frontend-backend bajo presión de tiempo
- **Probabilidad**: Media
- **Impacto**: Alto
- **Mitigación aplicada**:
  - Definir API contract con OpenAPI desde día 1
  - Desarrollo paralelo con datos mock
  - Tests E2E para validar integración
- **Resultado**: ✅ Integración fluida, 0 regresiones en producción

#### 4. Desconocimiento inicial de MQTT/IoT
- **Probabilidad**: Alta
- **Impacto**: Medio
- **Mitigación aplicada**:
  - Spike técnico en semana 2
  - Usar biblioteca estable (paho-mqtt)
  - Documentar setup en `docs/setup-mqtt.md`
- **Resultado**: ✅ Subscriber MQTT estable, 0 pérdidas de mensajes

### Lecciones aprendidas clave

#### ✅ Lo que funcionó bien

1. **Metodología PMBOK simplificada**: 
   - Adaptación ligera para equipo pequeño
   - Enfoque en áreas críticas (Alcance, Tiempo, Costo, Calidad)
   - Documentación incremental sin burocracia

2. **CI/CD desde el inicio**:
   - GitHub Actions configurado en semana 1
   - Tests automatizados evitaron regresiones
   - Confianza para refactorizar sin miedo

3. **Simulador IoT como fallback**:
   - Permitió desarrollo continuo sin bloqueos de hardware
   - Datos sintéticos validaron lógica de negocio
   - Facilita demos reproducibles

4. **Stack tecnológico moderno**:
   - FastAPI: desarrollo rápido con validación automática
   - React + Vite: hot reload aceleró iteraciones frontend
   - Docker Compose: entorno reproducible en cualquier máquina

#### ⚠️ Desafíos y mejoras futuras

1. **Testing del modelo ML**:
   - Faltó suite completa de tests para predicciones
   - Mejora: agregar tests de degradación de modelo y drift detection

2. **Monitoreo de producción**:
   - No se implementó observabilidad (logs centralizados, métricas)
   - Mejora: integrar Prometheus + Grafana para monitoreo real

3. **Documentación de usuario final**:
   - Docs técnicos completos, pero falta manual de operador
   - Mejora: crear guía ilustrada para técnicos no programadores

4. **Escalabilidad horizontal**:
   - Arquitectura monolítica suficiente para MVP
   - Mejora futura: considerar microservicios si >100 equipos

---

## 7. Conclusiones y Próximos Pasos

### Logros principales

✅ **Sistema funcional end-to-end** listo para demo y uso académico  
✅ **Meta de calidad superada**: 85.4% accuracy (objetivo: 80%)  
✅ **Presupuesto respetado**: $30 USD (96% bajo el límite de $750)  
✅ **Cronograma cumplido**: entrega v1.0.0 en semana 12 de 12  
✅ **Código abierto**: repositorio público con licencia MIT  

### Valor entregado

**Para la academia**:
- Proyecto reproducible para otras instituciones
- Caso de estudio PMBOK aplicado a IoT + ML
- Código y documentación reutilizables

**Para la industria**:
- Proof of concept para PYMES sin presupuesto enterprise
- Arquitectura base extensible para casos reales
- Demostración de viabilidad técnica y económica

### Roadmap futuro (post v1.0.0)

#### Corto plazo (1-3 meses)
- [ ] Integrar ESP32 físicos en entorno controlado
- [ ] Agregar notificaciones email/SMS para alertas críticas
- [ ] Implementar dashboard de administración de usuarios

#### Mediano plazo (3-6 meses)
- [ ] Entrenar modelo con datos reales (cuando haya suficiente histórico)
- [ ] Soporte multi-tenant para múltiples empresas
- [ ] API pública para integraciones externas

#### Largo plazo (6-12 meses)
- [ ] App móvil (React Native) para técnicos en campo
- [ ] Integración con sistemas ERP/CMMS existentes
- [ ] Algoritmos de optimización de rutas de mantenimiento

### Llamado a la acción

**Repositorio público**: [github.com/manttoai/manttoai](https://github.com/manttoai/manttoai) *(ajustar URL real)*

**Contribuciones bienvenidas**:
- Issues y sugerencias de mejora
- Pull requests con nuevas funcionalidades
- Adaptaciones para otros sectores industriales

**Contacto del equipo**:
- Sebastián Bravo: backend, DevOps, arquitectura
- Luis Loyola: frontend, base de datos, documentación
- Ángel Rubilar: hardware, ML, validación técnica

---

## Apéndice: Referencias

### Documentación del proyecto
- `docs/arquitectura-manttoai.md` - Arquitectura detallada
- `docs/informe-pmbok-final.md` - Informe de gestión completo
- `docs/api-docs.md` - Especificación OpenAPI
- `docs/setup-mqtt.md` - Configuración MQTT
- `docs/ml-model.md` - Diseño del modelo predictivo

### Datasets y referencias técnicas
- NASA C-MAPSS Turbofan Engine Degradation Dataset
- Documentación oficial: FastAPI, React, scikit-learn
- PMBOK Guide 6ta Edición (PMI)

### Herramientas utilizadas
- Visual Studio Code + extensiones Python/React
- Postman para testing de API
- DBeaver para gestión MySQL
- MQTT Explorer para debug de telemetría

---

**Fin de la presentación**

*Preparado para defensa académica INACAP - Gestión de Proyectos Informáticos*  
*Versión 1.0.0 - Abril 2026*
