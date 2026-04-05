# Validación de 3 nodos ESP32 en paralelo

Guía operativa para demostrar el escenario físico objetivo del MVP: **3 nodos ESP32 publicando simultáneamente** y visibles en backend/dashboard.

## Objetivo

Validar de forma repetible que los equipos `1`, `2` y `3`:

1. publican al broker MQTT,
2. persisten lecturas en backend,
3. aparecen con telemetría en dashboard.

## Precondiciones

- Stack levantado (`make up`).
- Credenciales MQTT configuradas y archivo `mosquitto/passwd` generado (`make setup-mqtt-creds`).
- 3 placas ESP32 con firmware cargado y sensores operativos.
- Usuario de demo válido para consultar API (`admin@manttoai.local` por defecto del seed).

## Configuración de nodos

En `iot/firmware/manttoai_sensor/config.h`, usar mismo broker/credenciales y diferente `EQUIPO_ID` por nodo:

- Nodo A -> `EQUIPO_ID=1`
- Nodo B -> `EQUIPO_ID=2`
- Nodo C -> `EQUIPO_ID=3`

## Paso 1 — Evidencia de publicación simultánea en broker

```bash
mosquitto_sub -h <broker> -u <mqtt_user> -P <mqtt_pass> -t "manttoai/#" -v
```

Esperado: mensajes intercalados para los topics:

- `manttoai/equipo/1/lecturas`
- `manttoai/equipo/2/lecturas`
- `manttoai/equipo/3/lecturas`

## Paso 2 — Evidencia de persistencia para 3 equipos

Desde la raíz del repo:

```bash
python scripts/verify_three_nodes.py --api-url "http://localhost:8000" --equipos "1,2,3" --auth-email "admin@manttoai.local" --ventana-minutos 10 --max-desfase-segundos 120
```

También disponible como:

```bash
make verify-3-nodes
```

> Si no definís `VERIFY_ADMIN_PASSWORD`, el script pedirá password en un prompt oculto.
> Para ejecución no interactiva, exportá `VERIFY_ADMIN_PASSWORD` antes del comando.

## Paso 3 — Evidencia visual en dashboard

Abrir frontend y verificar en Dashboard:

- sección **Estado por equipo** con los 3 equipos,
- temperatura no nula para `1`, `2`, `3`,
- tabla **Últimas lecturas** mostrando entradas de los 3 equipos.

## Plantilla mínima de evidencia (para informe/defensa)

Completar esta tabla al ejecutar la prueba:

| Ítem | Evidencia | Estado |
|---|---|---|
| 3 topics simultáneos en `mosquitto_sub` | Captura terminal broker | ☐ |
| Persistencia de equipos 1/2/3 | Salida `verify_three_nodes.py` | ☐ |
| Dashboard con 3 equipos activos | Captura frontend | ☐ |
| Fecha/hora de ejecución registrada | Timestamp en reporte | ☐ |

> Recomendación: guardar capturas con nombre `evidencia-3-nodos-YYYYMMDD-HHMM` para trazabilidad.
