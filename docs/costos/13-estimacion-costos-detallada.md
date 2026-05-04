# 13. Estimación de Costos Detallada

## Costos del Plan de Negocios (Evaluación 3 — Gestión de Costos)

ManttoAI como empresa real opera con un capital inicial de **$3.000.000 CLP** aportado por los 3 socios fundadores. La estimación es ascendente (bottom-up) para activos y análoga para honorarios profesionales.

### Inversión inicial Año 1

| Categoría | Ítem | Justificación | Monto (CLP) |
|-----------|------|---------------|-------------|
| Equipamiento físico | 6 kits ESP32 + sensores + cableado | 2 kits por rubro (industrial, agrícola, comercial). MercadoLibre CL. | $165.000 |
| Infraestructura digital | Droplet 2GB RAM (Digital Ocean, São Paulo) | API + MQTT + Frontend en Docker Compose | $163.200 |
| Infraestructura digital | PostgreSQL gestionada (Digital Ocean) | Base de datos relacional para telemetría | $109.200 |
| Infraestructura digital | Spaces 250GB (Digital Ocean) | Almacenamiento de objetos para backups y datos históricos | $43.800 |
| Infraestructura digital | Dominio .cl (NIC Chile) | Registro anual | $11.400 |
| **Total activos** | | | **$492.600** |

### Costos operacionales mensuales Año 1

| Ítem | Monto mensual (CLP) | Tipo |
|------|---------------------|------|
| Infraestructura Digital Ocean (São Paulo) | $25.600 | Fijo |
| Contador externo (contadoresenlinea.cl, IVA incl.) | $89.000 | Fijo |
| Abogado externo (3 servicios/año prorrateado) | $62.500 | Variable |
| Domicilio comercial virtual (OficinVirtual.cl) | $5.000 | Fijo |
| Dominio y herramientas digitales | $5.000 | Fijo |
| **Total mensual** | **$187.100** | |
| **Total anual** | **$2.245.200** | |

### Proyección de ingresos por suscripción

| Etapa | Clientes activos | Precio mensual por rubro | Ingreso mensual |
|-------|------------------|--------------------------|-----------------|
| Año 1 — Validación | 0 – 4 | $88.000 | $0 – $352.000 |
| Año 2 — Crecimiento | 10 – 12 | $88.000 | $880.000 – $1.056.000 |
| Año 3 — Consolidación | 20 – 22 | $88.000 | $1.760.000 – $1.936.000 |

---

## Costos del Prototipo Académico (referencia histórica)

El prototipo técnico implementado en este repositorio usó un presupuesto real de **USD $98**:

| Categoría | Ítem | Costo Real (USD) |
|-----------|------|------------------|
| Hardware | 3× ESP32 DevKit v1 | $30 |
| Hardware | 3× DHT22 | $18 |
| Hardware | 3× MPU-6050 | $10 |
| Infraestructura | VPS Hetzner CX22 (2 meses) | $40 |
| **Total real** | | **$98** |

El presupuesto académico simulado (CLP $9.790.000) incluía honorarios del equipo y reserva de contingencia, y fue usado únicamente para la evaluación académica inicial.

---

*Fuentes: Digital Ocean Pricing 2026, MercadoLibre CL, contadoresenlinea.cl, NIC Chile, OficinVirtual.cl, Hetzner Cloud.*
