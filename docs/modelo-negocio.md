# ManttoAI Predictivo — Modelo de Negocio y Estrategia

> Documento de soporte para la defensa del Proyecto de Título.
> Ubicación recomendada en el repo: `docs/modelo-negocio.md`

**Nota:** Este documento está alineado con el informe enterprise del proyecto,
que contempla infraestructura AWS, equipo de 4 personas y un presupuesto total
de inversión de CLP $9.790.000 (~USD 10.640).

---

## 1. Resumen Ejecutivo

ManttoAI Predictivo es una plataforma SaaS de mantenimiento predictivo industrial diseñada específicamente para PyMEs y medianas empresas latinoamericanas que necesitan capacidades enterprise pero no pueden pagar las soluciones tradicionales como SAP PM, IBM Maximo o Oracle Asset Management.

**Propuesta de valor en una frase:** Mantenimiento predictivo industrial con capacidades enterprise (IoT + IA + Cloud) a una fracción del costo de las soluciones tradicionales, con implementación rápida y sin vendor lock-in.

**Tracción actual:** Prototipo funcional validado en entorno controlado, modelo ML con F1-Score ≥ 85%, infraestructura desplegada en AWS Cloud.

---

## 2. El Problema

### 2.1 Contexto del mercado industrial en LATAM

Las empresas industriales en Chile y América Latina enfrentan tres realidades simultáneas:

1. **Mantenimiento reactivo dominante:** El 70% de las industrias medianas en LATAM aún hacen mantenimiento correctivo (reparar cuando se rompe), no predictivo.

2. **Costo de paradas no planificadas:** Una hora de parada en una línea de producción industrial cuesta entre USD 1.000 y USD 50.000 dependiendo del sector. Para una mediana empresa, una falla mayor puede representar el margen mensual completo de toda la planta.

3. **Soluciones enterprise inaccesibles:** Las plataformas que sí resuelven esto cuestan entre USD 3.000 y USD 15.000 mensuales, requieren consultores certificados para implementarlas, contratos anuales y meses de despliegue. Una mediana empresa chilena de 50 empleados no puede absorber ese costo ni esa complejidad.

### 2.2 La brecha del mercado

Existe un segmento masivo y desatendido: **empresas industriales medianas con equipos críticos pero sin presupuesto enterprise**. Estas empresas necesitan mantenimiento predictivo real (no soluciones de juguete), pero no tienen las opciones que tienen las grandes corporaciones.

---

## 3. La Solución: ManttoAI Predictivo

### 3.1 Qué ofrecemos

Una plataforma de mantenimiento predictivo completa que incluye:

- **Hardware IoT industrial:** Sensores ESP32 con DHT22 (temperatura) y MPU-6050 (vibración), dimensionados para resistir condiciones de planta
- **Pipeline de datos en AWS Cloud:** Ingesta, transformación y almacenamiento estructurado en infraestructura escalable
- **Modelo de Machine Learning validado:** Random Forest entrenado con F1-Score ≥ 85%, listo para inferencia en producción
- **Dashboard web profesional:** Interfaz responsiva, accesible desde cualquier navegador, con visualización en tiempo real
- **Sistema de alertas automáticas:** Notificaciones por email cuando un equipo entra en zona de riesgo
- **Trazabilidad técnica completa:** Historial de lecturas, alertas, predicciones y mantenciones para auditoría
- **Soporte para hasta 50 usuarios concurrentes:** Validado mediante pruebas de carga

### 3.2 Diferenciadores clave

| Característica | ManttoAI | SAP PM / IBM Maximo |
|----------------|----------|---------------------|
| Precio mensual (plan base) | USD 500 | USD 3.000 - 15.000 |
| Tiempo de implementación | 1-2 semanas | 3-6 meses |
| Requiere consultores externos | No | Sí |
| Vendor lock-in | No (stack abierto) | Sí (propietario) |
| Foco regional | LATAM | Global |
| Curva de aprendizaje | Días | Semanas/meses |
| Contratos anuales obligatorios | No | Sí |

**El posicionamiento honesto:** ManttoAI es entre 6 y 30 veces más barato que las soluciones enterprise, dependiendo del plan que elija el cliente. No es "más barato pero peor" — es la misma capacidad técnica núcleo (IoT + ML + Dashboard + Alertas) sin las capas de complejidad y sobrecosto que justifica el precio enterprise.

---

## 4. Modelo de Negocio SaaS

### 4.1 Estructura de Pricing en 3 Tiers

**Plan Starter — USD 500/mes**

Para empresas que recién empiezan con mantenimiento predictivo.

Incluye:
- Hasta 5 nodos ESP32 monitoreando equipos
- Dashboard web con hasta 10 usuarios
- Alertas por email
- Modelo ML estándar
- Soporte por email (respuesta en 48hs)
- Backups diarios automáticos

**Plan Professional — USD 1.200/mes** ⭐ Recomendado

Para empresas con operaciones críticas que necesitan respuesta rápida.

Incluye todo lo del Starter, más:
- Hasta 15 nodos ESP32
- Dashboard web con usuarios ilimitados
- Modelo ML personalizado con datos del cliente
- Soporte prioritario (respuesta en 8hs)
- SLA de 99.5% uptime
- Reportes mensuales personalizados
- 1 sesión de capacitación on-site al onboarding

**Plan Enterprise — USD 3.000/mes**

Para medianas empresas con múltiples plantas o equipos críticos de alto valor.

Incluye todo lo del Professional, más:
- Nodos ESP32 ilimitados
- SLA de 99.9% uptime
- Account manager dedicado
- Integración custom con sistemas existentes (ERPs propios)
- Capacitación trimestral
- Soporte 24/7 para emergencias
- Reportes ejecutivos mensuales

### 4.2 Segmento objetivo

**Cliente ideal:**
- Empresa industrial mediana en LATAM (Chile, Argentina, Perú, Colombia, México)
- 30 a 200 empleados
- Sectores: manufactura, agroindustria, minería pequeña/mediana, alimentación, química
- Tiene al menos 5-10 equipos críticos cuyas fallas generan paradas costosas
- Presupuesto operacional disponible pero no para soluciones enterprise tradicionales
- Decisión de compra: gerente de operaciones o gerente de planta

### 4.3 Unit Economics realista (Plan Professional como referencia)

| Métrica | Valor (USD) |
|---------|-------------|
| Precio mensual (ARPU) | $1.200 |
| Costo de infraestructura AWS por cliente | -$200 |
| Costo de soporte estimado (prorrateado) | -$150 |
| Costo de licencias y herramientas (prorrateado) | -$50 |
| **Margen bruto por cliente** | **$800/mes (~67%)** |
| Costo de adquisición estimado (CAC) | $1.500 |
| Período de recuperación del CAC | 1.9 meses |
| LTV estimado (24 meses) | $19.200 |
| **Ratio LTV/CAC** | **12.8x** |

### 4.4 Punto de Breakeven del Proyecto

Inversión inicial total del proyecto (según informe enterprise):

| Concepto | Costo (CLP) | Costo (USD aprox.) |
|----------|-------------|--------------------|
| Infraestructura cloud AWS (6 meses iniciales) | $1.200.000 | $1.300 |
| Sensores IoT prototipo y testing | $800.000 | $870 |
| Equipo de desarrollo (4 personas, 6 meses) | $6.000.000 | $6.520 |
| Licencias y herramientas | $300.000 | $325 |
| QA y pruebas | $400.000 | $435 |
| Documentación y entregables | $200.000 | $215 |
| Contingencia (10%) | $890.000 | $970 |
| **Total inversión inicial** | **$9.790.000** | **~$10.640** |

**Análisis de breakeven:**

Con el Plan Professional como referencia (margen bruto USD 800/mes por cliente):

- **Para recuperar la inversión inicial:** se necesitan 14 clientes-mes
- **Escenario A (lento):** 5 clientes en el mes 6 → breakeven en mes 9
- **Escenario B (medio):** 10 clientes en el mes 6 → breakeven en mes 7
- **Escenario C (optimista):** 15 clientes en el mes 6 → breakeven en mes 6

Una vez alcanzado el breakeven, cada cliente adicional contribuye USD 800/mes en margen bruto a la operación.

---

## 5. Análisis de Mercado

### 5.1 Tamaño del mercado

El mercado global de mantenimiento predictivo está valorado en aproximadamente USD 15 mil millones para 2027, con un CAGR del 25%. El segmento de empresas medianas representa la parte de mayor crecimiento, ya que las grandes industrias ya están penetradas por los players enterprise.

**Mercado direccionable en LATAM:** Estimación conservadora de 30.000+ empresas industriales medianas potencialmente compradoras solo en los 5 países objetivo (Chile, Argentina, Perú, Colombia, México).

### 5.2 Competencia

**Competencia directa enterprise (no compite por el mismo segmento):**
- IBM Maximo (USD 5.000-15.000/mes)
- SAP Plant Maintenance (USD 8.000+/mes con licencias)
- Oracle Asset Management (USD 6.000+/mes)
- Fiix by Rockwell (USD 1.500-4.000/mes)
- UpKeep (USD 800-2.500/mes)

**Competencia indirecta:**
- Mantenimiento reactivo tradicional (status quo, gratis pero con costos ocultos enormes)
- Hojas de Excel y planillas manuales
- Consultoras de ingeniería que venden auditorías one-shot (USD 5.000-20.000 por auditoría)

### 5.3 Ventaja competitiva

ManttoAI no compite contra SAP en el segmento enterprise — pierde de cabeza. Compite contra dos cosas:

1. **El status quo del mantenimiento reactivo** en empresas que nunca van a pagar SAP
2. **Players medianos como Fiix y UpKeep** ofreciendo mejor precio, foco LATAM y stack abierto

Las ventajas concretas son:

1. **Precio accesible para el segmento mediano:** Una empresa que pierde USD 10.000 en una sola parada paga ManttoAI Professional por casi un año con eso
2. **Simplicidad operacional:** Un técnico de mantenimiento puede operar el dashboard sin capacitación extensa
3. **Foco regional:** Soporte en español, conocimiento del contexto LATAM (cortes de luz, conectividad limitada, normativas locales)
4. **Sin vendor lock-in:** Stack abierto, datos exportables, sin contratos leoninos de 3 años
5. **Implementación rápida:** 1-2 semanas vs 3-6 meses de soluciones enterprise

---

## 6. Roadmap Post-MVP

### Milestone 1 — Validación con primeros pilotos (Q3 2025)

**Objetivo:** Conseguir 2-3 clientes piloto que paguen el Plan Professional y usar su feedback para priorizar el desarrollo.

**Alcance técnico actual (lo que hay hoy):**
- Arquitectura **single-tenant por diseño** para los pilotos
- Cada cliente tiene su instancia dedicada en AWS
- Onboarding manual del cliente (configurar equipos, umbrales, usuarios, capacitación)
- Soporte directo del equipo fundador

**Por qué single-tenant en esta etapa:** Es la decisión correcta cuando tenés 0-3 clientes. Construir multi-tenencia sin clientes reales es sobre-ingeniería pura. Multi-tenant introduce complejidad de aislamiento de datos, gestión de permisos cross-tenant, billing por uso, escalado por cliente — todos problemas que solo valen la pena resolver cuando tenés clientes que los justifiquen. Aprovechamos la flexibilidad de AWS para levantar instancias separadas con automatización mínima.

**Métricas de éxito del milestone:**
- 2-3 clientes pagando Plan Professional (USD 1.200/mes c/u)
- 30 días sin caídas críticas
- Al menos 2 casos de éxito documentados (alertas que evitaron fallas reales con ROI medible)
- NPS > 40 en encuestas de satisfacción

### Milestone 2 — Escalar a 5-10 clientes (Q4 2025 / Q1 2026)

**Objetivo:** Validar que el modelo se puede repetir con clientes de distintos sectores.

**Cambios técnicos:**
- **Implementar multi-tenancy real** (acá sí tiene sentido)
- Aislamiento de datos por cliente con esquemas separados
- Onboarding semi-automatizado (formulario → provisioning automático)
- Dashboard de admin para el equipo de ManttoAI
- Optimización de costos AWS mediante recursos compartidos

**Por qué ahora sí:** Con 5+ clientes, el costo de mantener instancias AWS separadas se vuelve insostenible. La complejidad de multi-tenant se justifica porque reduce significativamente el costo operacional por cliente.

**Impacto en unit economics:** Reducción del costo de infraestructura AWS por cliente de USD 200/mes a aproximadamente USD 80/mes, mejorando el margen bruto del Plan Professional del 67% al 77%.

### Milestone 3 — Automatización de billing y self-service (Q2 2026)

**Objetivo:** Eliminar la fricción del cobro mensual manual y permitir self-service.

**Cambios técnicos:**
- Integración con Stripe (clientes internacionales) y MercadoPago (LATAM)
- Suscripciones recurrentes automáticas
- Self-service para upgrade/downgrade entre planes Starter/Professional/Enterprise
- Facturación automática con cumplimiento tributario por país
- Portal de cliente para gestión de su cuenta

**Cuándo se justifica:** Cuando el tiempo gastado en cobrar manualmente excede el costo de implementar la integración. Estimación: a partir de 8-10 clientes activos.

### Milestone 4 — Expansión regional (2026+)

**Objetivo:** Replicar el modelo en otros países LATAM.

**Trabajo necesario:**
- Localización de moneda y facturación por país
- Cumplimiento tributario local (boleta electrónica Chile, factura electrónica México, etc.)
- Partnerships con distribuidores locales en cada país
- Marketing localizado por sector
- Soporte horario por zona

---

## 7. Estado Actual del Proyecto

### Lo que está implementado y funcionando

- **Hardware IoT:** ESP32 + DHT22 + MPU-6050 con firmware completo, validado en entorno controlado
- **Backend FastAPI:** API REST completa con autenticación JWT y endpoints documentados
- **Pipeline de datos en AWS:** Ingesta, transformación y almacenamiento en infraestructura cloud
- **Base de datos:** Esquema normalizado con todas las tablas operativas
- **MQTT:** Pipeline completo ESP32 → Broker MQTT → Backend → Base de datos
- **Modelo de Machine Learning:** Random Forest entrenado con F1-Score ≥ 85% validado en cross-validation 5-fold
- **Dashboard React:** Interfaz funcional con gráficos en tiempo real
- **Alertas por email:** Sistema SMTP funcionando
- **Infraestructura:** Desplegado en AWS Cloud con CI/CD vía GitHub Actions
- **Pruebas:** Cobertura de tests del 70% en el backend, validación con 50 usuarios concurrentes
- **Documentación:** PMBOK completo, manual de usuario, documentación técnica de API

### Inversión realizada en el prototipo

| Categoría | Inversión (USD) |
|-----------|-----------------|
| Infraestructura AWS Cloud (6 meses) | $1.300 |
| Hardware IoT (sensores prototipo) | $870 |
| Equipo de desarrollo (4 personas, sueldos simulados) | $6.520 |
| Licencias y herramientas | $325 |
| QA y pruebas | $435 |
| Documentación y entregables | $215 |
| Contingencia (10%) | $970 |
| **Total inversión inicial** | **$10.640** |

Esta inversión refleja el costo realista de desarrollar el prototipo en condiciones profesionales. Es la cifra a recuperar mediante las primeras ventas del producto.

---

## 8. Por Qué ManttoAI es Defendible Académicamente

Para la defensa del proyecto de título, los puntos clave a destacar son:

**Técnicos:**
- Sistema integrado completo: hardware IoT + backend cloud + ML + frontend + deploy automatizado
- Stack moderno y profesional (FastAPI, React, AWS, Docker, GitHub Actions)
- Modelo de Machine Learning real con F1-Score ≥ 85% validado
- Arquitectura preparada para escalar de single-tenant a multi-tenant
- Cumplimiento de PMBOK en gestión del proyecto
- Cobertura de tests del 70% con CI/CD funcional
- Soporte para 50 usuarios concurrentes validado

**De negocio:**
- Identificación de un mercado real y desatendido (USD 15B+ proyectado a 2027)
- Modelo de negocio claro con tres tiers de pricing diferenciados
- Unit economics defendibles (margen bruto 67%, ratio LTV/CAC 12.8x)
- Análisis de breakeven realista (14 clientes-mes para recuperar inversión)
- Roadmap escalonado que separa MVP de escalamiento
- Decisiones técnicas fundamentadas en restricciones reales
- Producto vendible: cualquier persona del jurado puede entender qué se vende y a quién

**De gestión:**
- Equipo de 4 personas con roles claros
- Cumplimiento de cronograma de 6 meses
- Presupuesto controlado con contingencia del 10% (CLP $9.790.000)
- Indicador CPI con seguimiento mensual para control de costos
- Documentación completa según estándares PMBOK

---

## 9. Pitch para la Defensa (estructura sugerida de slides)

1. **El problema** — Empresas industriales medianas pierden plata por no poder pagar soluciones de mantenimiento predictivo enterprise (USD 3.000-15.000/mes)
2. **El mercado** — USD 15B+ para 2027, segmento mediano desatendido en LATAM
3. **La solución** — ManttoAI: stack completo IoT + ML + Cloud Dashboard desde USD 500/mes
4. **Demo en vivo** — Mostrar el flujo: ESP32 → MQTT → Backend → ML → Dashboard → Alerta
5. **Modelo ML** — Random Forest, F1-Score ≥ 85%, cross-validation, métricas
6. **Arquitectura** — Diagrama del sistema en AWS, decisiones técnicas, justificación del single-tenant para MVP
7. **Modelo de negocio** — Pricing en 3 tiers, unit economics, ratio LTV/CAC
8. **Punto de breakeven** — 14 clientes-mes para recuperar la inversión inicial de USD 10.640
9. **Competencia** — Por qué no competimos con SAP sino contra el status quo y Fiix/UpKeep
10. **Roadmap** — Pilotos → multi-tenancy → billing automático → expansión regional
11. **Cierre** — Esto no es un trabajo académico, es un producto vendible con plan de negocio defendible
