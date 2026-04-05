# Manual de usuario

Manual operativo para usar el MVP web de ManttoAI durante demo académica.

## 1) Acceso a la aplicación

1. Abrir navegador en `http://localhost:5173`.
2. Iniciar sesión con usuario demo:
   - email (demo): `admin@manttoai.local`
   - password (demo): `Admin123!`

> Si las credenciales cambiaron en seed, usar las definidas en `backend/.env` (`SEED_ADMIN_*`).
> Estas credenciales son solo para entorno académico/demo.

## 2) Dashboard

En la vista principal se muestran:

- total de equipos monitoreados,
- alertas activas,
- equipos en riesgo,
- clasificación/probabilidad de falla más reciente.

Uso recomendado:

1. Confirmar que `total_equipos` sea mayor a 0.
2. Revisar si `equipos_en_riesgo` cambió tras simulación o predicción.

## 3) Equipos y detalle

Desde **Equipos**:

1. Seleccionar un equipo.
2. Verificar lecturas recientes (temperatura, humedad, vibración).
3. Revisar última predicción y mantenciones asociadas.

## 4) Alertas

Desde **Alertas**:

1. Revisar alertas no leídas.
2. Abrir detalle contextual (tipo y mensaje).
3. Marcar alertas como leídas para limpiar bandeja operativa.

## 5) Historial

Desde **Historial**:

1. Revisar trazabilidad de lecturas por equipo.
2. Validar mantenciones registradas en el tiempo.

## 6) Flujo recomendado de uso en demo

1. Ejecutar `make seed` para datos base.
2. Ejecutar `make simulate` para generar lecturas.
3. Verificar Dashboard y Alertas.
4. Ejecutar una predicción desde backend (`POST /predicciones/ejecutar/{equipo_id}`) y refrescar frontend.

## 7) Buenas prácticas de operación

- No usar entorno demo contra datos productivos.
- Registrar captura/pantalla de resultados para informe final.
- Antes de presentación, correr `bash scripts/smoke_test.sh`.
