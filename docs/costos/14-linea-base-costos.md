# 14. Línea Base de Costos

## Línea base del Plan de Negocios (Año 1)

La línea base de costos se construye según el Proceso 7.3 del PMBOK: estimaciones de actividades + reservas de contingencia + reserva de gestión.

| Componente | Monto (CLP) | % del capital |
|---|---|---|
| Activos Año 1 | $492.600 | 16,4% |
| Operación 12 meses | $2.245.200 | 74,8% |
| Reserva de contingencia (10% ingresos por suscripción) | Variable | — |
| Reserva de gestión (saldo del capital) | $262.200 | 8,7% |
| **Capital comprometido total** | **$3.000.000** | **100%** |

> La reserva de gestión cubre ~1.4 meses adicionales de operación sin ingresos. La reserva de contingencia del 10% sobre ingresos por suscripción se activa desde el primer cliente.

### Distribución mensual estimada (Curva S — Año 1)

| Mes | Gasto operacional | Acumulado | Hito |
|-----|-------------------|-----------|------|
| 1 | $679.700 (activos + ops) | $679.700 | Setup inicial, compra hardware, despliegue DO |
| 2 | $187.100 | $866.800 | Desarrollo MVP |
| 3 | $187.100 | $1.053.900 | Integración MQTT + ML |
| 4 | $187.100 | $1.241.000 | Testing y ajustes |
| 5 | $187.100 | $1.428.100 | Primeros clientes (validación) |
| 6 | $187.100 | $1.615.200 | Corte EVM semestral |
| 7 | $187.100 | $1.802.300 | |
| 8 | $187.100 | $1.989.400 | |
| 9 | $187.100 | $2.176.500 | |
| 10 | $187.100 | $2.363.600 | |
| 11 | $187.100 | $2.550.700 | |
| 12 | $187.100 | $2.737.800 | Cierre Año 1, corte EVM anual |

### Indicadores EVM objetivo

| Indicador | Fórmula | Meta |
|-----------|---------|------|
| CPI (Índice de Desempeño de Costos) | EV / AC | ≥ 0,95 |
| CV (Variación de Costos) | EV − AC | Sin 2 meses consecutivos negativos |
| EAC (Estimación a la Conclusión) | BAC / CPI | ≤ BAC × 1,10 |
| SV (Variación del Cronograma) | EV − PV | ≥ 0 |

### Acciones correctivas escalonadas

1. **Desviación 5–10%:** revisión del directorio, ajuste de gastos discrecionales.
2. **Desviación 10–20%:** postergación de equipos propios Año 2, uso de reserva de gestión.
3. **Desviación > 20%:** revisión de modelo de precios, rebaja de retiros proyectados.

---

## Línea base del Prototipo Académico (referencia histórica)

Presupuesto académico simulado: CLP $9.790.000 en 6 meses (incluye honorarios RRHH). Costo real de bolsillo: USD $98.

| Mes | Gasto planificado (simulado) | Acumulado |
|-----|------------------------------|-----------|
| 1 | $1.000.000 (Hardware inicial) | $1.000.000 |
| 2 | $1.500.000 (Setup y RRHH) | $2.500.000 |
| 3 | $1.600.000 (Desarrollo) | $4.100.000 |
| 4 | $1.600.000 (Integración ML/IoT) | $5.700.000 |
| 5 | $1.600.000 (Testing y Deploy) | $7.300.000 |
| 6 | $1.600.000 (Cierre y Defensa) | $8.900.000 |

*Nota: La reserva de contingencia ($890.000) se mantuvo intacta.*
