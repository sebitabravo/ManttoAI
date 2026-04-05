#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5173}"
EQUIPO_ID="${EQUIPO_ID:-1}"
SMOKE_WAIT_SECONDS="${SMOKE_WAIT_SECONDS:-90}"
SMOKE_ALLOW_REMOTE="${SMOKE_ALLOW_REMOTE:-false}"
TMP_FILES=()

cleanup_tmp_files() {
  local temp_file

  for temp_file in "${TMP_FILES[@]:-}"; do
    if [ -n "$temp_file" ]; then
      rm -f "$temp_file"
    fi
  done
}

trap cleanup_tmp_files EXIT

log() {
  printf "\n[smoke] %s\n" "$1"
}

error() {
  printf "\n[smoke][error] %s\n" "$1" >&2
  exit 1
}

require_command() {
  local command_name
  command_name="$1"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    error "Falta comando requerido: ${command_name}"
  fi
}

assert_safe_target() {
  if [[ "$API_URL" =~ ^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)(:[0-9]+)?(/.*)?$ ]]; then
    return
  fi

  if [ "$SMOKE_ALLOW_REMOTE" = "true" ]; then
    log "⚠️ Ejecutando smoke en API remota por SMOKE_ALLOW_REMOTE=true"
    return
  fi

  error "API_URL no-local detectada (${API_URL}). Usá SMOKE_ALLOW_REMOTE=true solo si querés forzar."
}

wait_for_backend() {
  local elapsed
  elapsed=0

  until curl --silent --show-error --fail "${API_URL}/health" >/dev/null 2>&1; do
    if [ "$elapsed" -ge "$SMOKE_WAIT_SECONDS" ]; then
      error "Backend no disponible en ${API_URL} después de ${SMOKE_WAIT_SECONDS}s"
    fi

    sleep 2
    elapsed=$((elapsed + 2))
  done
}

execute_prediction() {
  local response_file
  local status_code

  response_file="$(mktemp)"
  TMP_FILES+=("$response_file")
  status_code="$({
    curl \
      --silent \
      --show-error \
      --output "$response_file" \
      --write-out "%{http_code}" \
      -X POST "${API_URL}/predicciones/ejecutar/${EQUIPO_ID}"
  })"

  if [ "$status_code" = "503" ]; then
    log "Modelo no disponible, entrenando artefacto ML..."

    if ! docker compose exec backend python /app/app/ml/train.py; then
      error "Entrenamiento ML falló. Revisá logs con: docker compose logs backend"
    fi

    status_code="$({
      curl \
        --silent \
        --show-error \
        --output "$response_file" \
        --write-out "%{http_code}" \
        -X POST "${API_URL}/predicciones/ejecutar/${EQUIPO_ID}"
    })"
  fi

  if [ "$status_code" != "201" ]; then
    cat "$response_file" >&2
    rm -f "$response_file"
    error "No se pudo ejecutar predicción (HTTP ${status_code})"
  fi

  cat "$response_file"
  rm -f "$response_file"
}

require_command docker
require_command make
require_command curl
require_command python3
assert_safe_target

log "Preparando entorno local"
make setup-env >/dev/null
make config >/dev/null
make up >/dev/null
wait_for_backend

log "Verificando frontend disponible"
curl --silent --show-error --fail "${FRONTEND_URL}" >/dev/null

log "Cargando datos base de demo"
make seed >/dev/null

log "Escenario 1/3: operación normal (simulador -> persistencia)"
make simulate >/dev/null

LECTURAS_JSON="$(curl --silent --show-error --fail "${API_URL}/lecturas?equipo_id=${EQUIPO_ID}")"
export LECTURAS_JSON
python3 - <<'PY'
import json
import os
import sys

lecturas = json.loads(os.environ["LECTURAS_JSON"])
if not isinstance(lecturas, list):
    print("Se esperaba lista de lecturas", file=sys.stderr)
    sys.exit(1)
if not lecturas:
    print("No hay lecturas persistidas para el equipo de prueba", file=sys.stderr)
    sys.exit(1)

print(f"Lecturas persistidas OK: {len(lecturas)}")
PY

log "Escenario 2/3: breach de umbral con alerta"
curl \
  --silent \
  --show-error \
  --fail \
  -X POST "${API_URL}/lecturas" \
  -H "Content-Type: application/json" \
  -d "{\"equipo_id\":${EQUIPO_ID},\"temperatura\":95.0,\"humedad\":30.0,\"vib_x\":2.5,\"vib_y\":2.5,\"vib_z\":25.0}" \
  >/dev/null

ALERTAS_JSON="$(curl --silent --show-error --fail "${API_URL}/alertas?equipo_id=${EQUIPO_ID}&solo_no_leidas=true&limite=100")"
export ALERTAS_JSON
python3 - <<'PY'
import json
import os
import sys

alertas = json.loads(os.environ["ALERTAS_JSON"])
if not isinstance(alertas, list):
    print("Se esperaba lista de alertas", file=sys.stderr)
    sys.exit(1)
if not alertas:
    print("No se generaron alertas no leídas para el equipo", file=sys.stderr)
    sys.exit(1)

tipos = {str(alerta.get("tipo", "")).lower() for alerta in alertas}
if "temperatura" not in tipos and "vibracion" not in tipos:
    print("Alertas sin tipo esperado de umbral", file=sys.stderr)
    sys.exit(1)

print(f"Alertas activas OK: {len(alertas)}")
PY

log "Escenario 3/3: predicción de riesgo visible en dashboard"
PREDICCION_JSON="$(execute_prediction)"
export PREDICCION_JSON

IS_RISK="$(python3 - <<'PY'
import json
import os

prediccion = json.loads(os.environ["PREDICCION_JSON"])
probabilidad = float(prediccion.get("probabilidad", 0.0))
print("1" if probabilidad >= 0.5 else "0")
PY
)"

if [ "$IS_RISK" != "1" ]; then
  log "Predicción inicial < 0.5, inyectando lectura extrema adicional"
  curl \
    --silent \
    --show-error \
    --fail \
    -X POST "${API_URL}/lecturas" \
    -H "Content-Type: application/json" \
    -d "{\"equipo_id\":${EQUIPO_ID},\"temperatura\":110.0,\"humedad\":20.0,\"vib_x\":3.5,\"vib_y\":3.5,\"vib_z\":30.0}" \
    >/dev/null

  PREDICCION_JSON="$(execute_prediction)"
  export PREDICCION_JSON
fi

SUMMARY_JSON="$(curl --silent --show-error --fail "${API_URL}/dashboard/resumen")"
export SUMMARY_JSON
export EQUIPO_ID
python3 - <<'PY'
import json
import os
import sys

equipo_id = int(os.environ["EQUIPO_ID"])
prediccion = json.loads(os.environ["PREDICCION_JSON"])
summary = json.loads(os.environ["SUMMARY_JSON"])

probabilidad = float(prediccion.get("probabilidad", 0.0))
if probabilidad < 0.5:
    print(
        f"Predicción sin riesgo suficiente para smoke ({probabilidad:.4f} < 0.5)",
        file=sys.stderr,
    )
    sys.exit(1)

if int(summary.get("total_equipos", 0)) < 3:
    print("Dashboard no refleja equipos demo esperados", file=sys.stderr)
    sys.exit(1)

equipos = summary.get("equipos", [])
equipo_objetivo = None
for equipo in equipos:
    if int(equipo.get("id", -1)) == equipo_id:
        equipo_objetivo = equipo
        break

if equipo_objetivo is None:
    print("Dashboard no incluye el equipo objetivo", file=sys.stderr)
    sys.exit(1)

if equipo_objetivo.get("ultima_probabilidad") is None:
    print("Dashboard no muestra probabilidad para el equipo objetivo", file=sys.stderr)
    sys.exit(1)

if int(summary.get("equipos_en_riesgo", 0)) < 1:
    print("Dashboard no marca equipos en riesgo", file=sys.stderr)
    sys.exit(1)

print(
    "Dashboard OK: "
    f"equipos={summary.get('total_equipos')} "
    f"alertas_activas={summary.get('alertas_activas')} "
    f"equipos_en_riesgo={summary.get('equipos_en_riesgo')} "
    f"prob_equipo={equipo_objetivo.get('ultima_probabilidad')}"
)
PY

log "Smoke test completado correctamente ✅"
