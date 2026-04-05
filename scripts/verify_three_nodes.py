#!/usr/bin/env python3
"""Valida evidencia mínima de 3 nodos publicando en paralelo."""

from __future__ import annotations

import argparse
import getpass
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from os import getenv
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
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
    parser.add_argument(
        "--token",
        default="",
        help=(
            "JWT token directo. Preferir VERIFY_ADMIN_TOKEN en entorno (más seguro). "
            "Usar '-' para leer el token desde un prompt oculto."
        ),
    )
    parser.add_argument("--auth-email", default="admin@manttoai.local")
    parser.add_argument(
        "--allow-insecure",
        action="store_true",
        help="Permite HTTP hacia hosts remotos (solo para entornos controlados).",
    )
    parser.add_argument("--output", default="")
    return parser.parse_args()


def is_local_host(hostname: str | None) -> bool:
    """Indica si el host corresponde a loopback/local."""

    if not hostname:
        return False
    return hostname.lower() in {"localhost", "127.0.0.1", "::1"}


def validate_api_url_security(api_url: str, allow_insecure: bool) -> None:
    """Valida esquema/host para evitar credenciales en claro por error."""

    parsed = urlparse(api_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("El --api-url debe usar http:// o https://")

    if not parsed.netloc:
        raise ValueError("El --api-url debe incluir host válido")

    if parsed.scheme == "http" and not is_local_host(parsed.hostname):
        warning = (
            "HTTP sobre host remoto puede exponer credenciales en tránsito. "
            "Preferí HTTPS"
        )
        if not allow_insecure:
            raise ValueError(f"{warning}. Si entendés el riesgo, usá --allow-insecure")

        print(f"ADVERTENCIA: {warning} (override activo por --allow-insecure)")


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


def format_http_error(context: str, exc: HTTPError) -> str:
    """Formatea errores HTTP con contexto y cuerpo resumido."""

    body = ""
    try:
        body = exc.read().decode("utf-8").strip()
    except Exception:
        body = ""

    body_suffix = f" Respuesta: {body[:220]}" if body else ""
    return f"{context} (HTTP {exc.code} {exc.reason}).{body_suffix}"


def resolve_auth_password() -> str:
    """Obtiene password desde entorno o prompt seguro."""

    env_password = (
        getenv("VERIFY_ADMIN_PASSWORD") or getenv("SEED_ADMIN_PASSWORD") or ""
    ).strip()
    if env_password:
        return env_password

    try:
        prompt = "Password de admin para /auth/login (input oculto): "
        password = getpass.getpass(prompt=prompt).strip()
    except (EOFError, KeyboardInterrupt) as exc:
        raise ValueError(
            "No se pudo leer password interactiva. Seteá VERIFY_ADMIN_PASSWORD."
        ) from exc

    if not password:
        raise ValueError(
            "Password vacía. Definí VERIFY_ADMIN_PASSWORD o ingresá una en el prompt."
        )

    return password


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


def resolve_auth_token(api_url: str, token: str, email: str) -> str:
    """Resuelve token JWT desde variable de entorno, argumento o login API.

    Orden de prioridad:
    1. Variable de entorno VERIFY_ADMIN_TOKEN (recomendado para CI/scripts).
    2. Argumento --token con valor '-': lee token desde prompt oculto.
    3. Argumento --token con valor explícito (visible en ps; evitar en producción).
    4. Login con email/password (prompt oculto o VERIFY_ADMIN_PASSWORD).
    """

    # 1) Variable de entorno: opción más segura para automatización
    env_token = (getenv("VERIFY_ADMIN_TOKEN") or "").strip()
    if env_token:
        return env_token

    # 2) Lectura oculta desde stdin cuando el usuario pasa '-'
    if token.strip() == "-":
        try:
            t = getpass.getpass(prompt="JWT token (input oculto): ").strip()
        except (EOFError, KeyboardInterrupt) as exc:
            raise ValueError(
                "No se pudo leer token interactivo. Seteá VERIFY_ADMIN_TOKEN."
            ) from exc
        if not t:
            raise ValueError(
                "Token vacío. Definí VERIFY_ADMIN_TOKEN o ingresá uno en el prompt."
            )
        return t

    # 3) Token explícito en CLI (sigue funcionando; visible en ps, evitar si es posible)
    if token.strip():
        return token.strip()

    # 4) Fallback: login con email/password
    password = resolve_auth_password()

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
        validate_api_url_security(args.api_url, allow_insecure=args.allow_insecure)
    except ValueError as exc:
        print(f"No se pudo validar --api-url: {exc}")
        return 1

    try:
        auth_token = resolve_auth_token(
            api_url=args.api_url,
            token=args.token,
            email=args.auth_email,
        )
    except HTTPError as exc:
        print(format_http_error("No se pudo obtener token desde /auth/login", exc))
        print("Verificá --api-url, --auth-email y credenciales de autenticación.")
        return 1
    except URLError as exc:
        print(f"No se pudo conectar al API durante login: {exc.reason}")
        return 1
    except ValueError as exc:
        print(f"No se pudo resolver token de autenticación: {exc}")
        return 1

    try:
        dashboard_map = build_dashboard_map(args.api_url, auth_token)
    except HTTPError as exc:
        print(format_http_error("No se pudo leer /dashboard/resumen", exc))
        return 1
    except URLError as exc:
        print(f"No se pudo conectar al API para leer /dashboard/resumen: {exc.reason}")
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
