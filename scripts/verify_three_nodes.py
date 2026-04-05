#!/usr/bin/env python3
"""Valida evidencia mínima de 3 nodos publicando en paralelo."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class EquipoCheck:
    """Resultado de validación por equipo."""

    equipo_id: int
    lectura_ok: bool
    dashboard_ok: bool
    timestamp: datetime | None
    temperatura: float | None
    detalle: str


def parse_args() -> argparse.Namespace:
    """Parsea argumentos para validación de demo 3 nodos."""

    parser = argparse.ArgumentParser(
        description="Validador de escenario 3 nodos ManttoAI"
    )
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--equipos", default="1,2,3")
    parser.add_argument("--ventana-minutos", type=int, default=10)
    parser.add_argument("--max-desfase-segundos", type=int, default=120)
    parser.add_argument("--token", default="")
    parser.add_argument("--auth-email", default="admin@manttoai.local")
    parser.add_argument("--auth-password", default="Admin123!")
    parser.add_argument("--output", default="")
    return parser.parse_args()


def parse_equipos(raw: str) -> list[int]:
    """Convierte lista CSV de IDs en enteros válidos."""

    equipos: list[int] = []
    for item in raw.split(","):
        item_clean = item.strip()
        if not item_clean:
            continue
        equipos.append(int(item_clean))

    if not equipos:
        raise ValueError("Debés indicar al menos un equipo en --equipos")

    return equipos


def fetch_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    token: str = "",
) -> dict | list:
    """Obtiene JSON vía HTTP usando librería estándar."""

    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=10) as response:  # nosec B310 - URL controlada por operador
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def parse_timestamp(value: str | None) -> datetime | None:
    """Parsea timestamp ISO8601 en UTC."""

    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


def build_dashboard_map(api_url: str, token: str) -> dict[int, dict]:
    """Construye mapa de resumen por equipo para validación rápida."""

    dashboard_payload = fetch_json(
        f"{api_url.rstrip('/')}/dashboard/resumen",
        token=token,
    )
    equipos_payload = (
        dashboard_payload.get("equipos", [])
        if isinstance(dashboard_payload, dict)
        else []
    )

    dashboard_map: dict[int, dict] = {}
    for equipo in equipos_payload:
        if not isinstance(equipo, dict):
            continue
        try:
            equipo_id = int(equipo.get("id"))
        except (TypeError, ValueError):
            continue
        dashboard_map[equipo_id] = equipo

    return dashboard_map


def validate_equipo(
    api_url: str,
    equipo_id: int,
    dashboard_map: dict[int, dict],
    cutoff: datetime,
    token: str,
) -> EquipoCheck:
    """Valida lectura reciente y presencia en dashboard para un equipo."""

    try:
        lectura_payload = fetch_json(
            f"{api_url.rstrip('/')}/lecturas/latest/{equipo_id}",
            token=token,
        )
    except HTTPError as exc:
        return EquipoCheck(
            equipo_id=equipo_id,
            lectura_ok=False,
            dashboard_ok=False,
            timestamp=None,
            temperatura=None,
            detalle=f"Lectura no disponible (HTTP {exc.code})",
        )
    except URLError as exc:
        return EquipoCheck(
            equipo_id=equipo_id,
            lectura_ok=False,
            dashboard_ok=False,
            timestamp=None,
            temperatura=None,
            detalle=f"No se pudo conectar al API ({exc.reason})",
        )

    timestamp = parse_timestamp(
        lectura_payload.get("timestamp") if isinstance(lectura_payload, dict) else None
    )
    temperatura = None
    if isinstance(lectura_payload, dict):
        try:
            temperatura = float(lectura_payload.get("temperatura"))
        except (TypeError, ValueError):
            temperatura = None

    lectura_ok = (
        timestamp is not None and timestamp >= cutoff and temperatura is not None
    )
    dashboard_equipo = dashboard_map.get(equipo_id)
    dashboard_ok = (
        dashboard_equipo is not None
        and dashboard_equipo.get("ultima_temperatura") is not None
    )

    if lectura_ok and dashboard_ok:
        detalle = "OK"
    elif not lectura_ok and not dashboard_ok:
        detalle = "Sin lectura reciente y sin temperatura visible en dashboard"
    elif not lectura_ok:
        detalle = "Sin lectura reciente válida"
    else:
        detalle = "Dashboard no muestra temperatura para este equipo"

    return EquipoCheck(
        equipo_id=equipo_id,
        lectura_ok=lectura_ok,
        dashboard_ok=dashboard_ok,
        timestamp=timestamp,
        temperatura=temperatura,
        detalle=detalle,
    )


def format_timestamp(value: datetime | None) -> str:
    """Formatea timestamp UTC para reporte."""

    if value is None:
        return "N/A"
    return value.isoformat().replace("+00:00", "Z")


def build_markdown_report(
    checks: list[EquipoCheck],
    now: datetime,
    ventana_minutos: int,
    max_desfase_segundos: int,
    simultaneo_ok: bool,
    desfase_real: float | None,
) -> str:
    """Construye reporte markdown reutilizable para evidencia."""

    lines = [
        "# Evidencia validación 3 nodos",
        "",
        f"- Fecha UTC: {now.isoformat().replace('+00:00', 'Z')}",
        f"- Ventana de validación: {ventana_minutos} minutos",
        f"- Umbral de simultaneidad: {max_desfase_segundos} segundos",
        "",
        "## Resultado por equipo",
        "",
        "| Equipo | Lectura reciente | Dashboard con temperatura | Timestamp lectura | Temperatura | Detalle |",
        "|---|---|---|---|---|---|",
    ]

    for check in checks:
        lines.append(
            "| "
            f"{check.equipo_id} | "
            f"{'✅' if check.lectura_ok else '❌'} | "
            f"{'✅' if check.dashboard_ok else '❌'} | "
            f"{format_timestamp(check.timestamp)} | "
            f"{check.temperatura if check.temperatura is not None else 'N/A'} | "
            f"{check.detalle} |"
        )

    lines.extend(
        [
            "",
            "## Simultaneidad",
            "",
            f"- Resultado: {'✅' if simultaneo_ok else '❌'}",
            f"- Desfase real entre timestamps más reciente y más antiguo: {desfase_real:.1f}s"
            if desfase_real is not None
            else "- Desfase real: N/A",
        ]
    )

    return "\n".join(lines) + "\n"


def resolve_auth_token(api_url: str, token: str, email: str, password: str) -> str:
    """Resuelve token JWT desde argumento directo o login API."""

    if token.strip():
        return token.strip()

    login_payload = fetch_json(
        f"{api_url.rstrip('/')}/auth/login",
        method="POST",
        payload={"email": email, "password": password},
    )

    if not isinstance(login_payload, dict):
        raise ValueError("Respuesta inválida de /auth/login")

    access_token = str(login_payload.get("access_token") or "").strip()
    if not access_token:
        raise ValueError("No se recibió access_token desde /auth/login")

    return access_token


def main() -> int:
    """Ejecuta validación de 3 nodos y retorna código de salida."""

    args = parse_args()
    equipos = parse_equipos(args.equipos)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=args.ventana_minutos)

    try:
        auth_token = resolve_auth_token(
            api_url=args.api_url,
            token=args.token,
            email=args.auth_email,
            password=args.auth_password,
        )
    except (HTTPError, URLError, ValueError) as exc:
        print(f"No se pudo resolver token de autenticación: {exc}")
        return 1

    try:
        dashboard_map = build_dashboard_map(args.api_url, auth_token)
    except (HTTPError, URLError) as exc:
        print(f"No se pudo leer /dashboard/resumen: {exc}")
        return 1

    checks = [
        validate_equipo(args.api_url, equipo_id, dashboard_map, cutoff, auth_token)
        for equipo_id in equipos
    ]

    timestamps = [check.timestamp for check in checks if check.timestamp is not None]
    desfase_real = None
    simultaneo_ok = False
    if len(timestamps) >= 2:
        delta = max(timestamps) - min(timestamps)
        desfase_real = delta.total_seconds()
        simultaneo_ok = desfase_real <= args.max_desfase_segundos
    elif len(timestamps) == 1:
        desfase_real = 0.0
        simultaneo_ok = True

    all_lecturas_ok = all(check.lectura_ok for check in checks)
    all_dashboard_ok = all(check.dashboard_ok for check in checks)
    success = all_lecturas_ok and all_dashboard_ok and simultaneo_ok

    report = build_markdown_report(
        checks=checks,
        now=now,
        ventana_minutos=args.ventana_minutos,
        max_desfase_segundos=args.max_desfase_segundos,
        simultaneo_ok=simultaneo_ok,
        desfase_real=desfase_real,
    )

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Reporte guardado en: {output_path}")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
