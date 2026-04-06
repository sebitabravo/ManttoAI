"""Tests unitarios para scripts/verify_three_nodes.py."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "verify_three_nodes.py"


def _load_verify_module():
    """Carga el script de verificación como módulo importable."""

    module_name = "verify_three_nodes_script_test"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def verify_module():
    """Entrega el módulo del script para pruebas unitarias."""

    return _load_verify_module()


def test_parse_equipos_parsea_csv_con_espacios(verify_module):
    """Valida parseo de IDs CSV con espacios y comas."""

    assert verify_module.parse_equipos(" 1, 2 ,3 ") == [1, 2, 3]


def test_parse_equipos_rechaza_lista_vacia(verify_module):
    """Valida error cuando no se envía ningún equipo válido."""

    with pytest.raises(ValueError, match="al menos un equipo"):
        verify_module.parse_equipos(" , ")


def test_validate_api_url_security_rechaza_http_remoto_sin_override(verify_module):
    """Valida rechazo de HTTP remoto cuando falta --allow-insecure."""

    with pytest.raises(ValueError, match="allow-insecure"):
        verify_module.validate_api_url_security(
            "http://demo.manttoai.local", allow_insecure=False
        )


def test_validate_api_url_security_acepta_http_local_o_override(verify_module):
    """Valida aceptación de localhost o override explícito."""

    verify_module.validate_api_url_security(
        "http://localhost:8000", allow_insecure=False
    )
    verify_module.validate_api_url_security(
        "http://demo.manttoai.local", allow_insecure=True
    )


def test_parse_timestamp_soporta_iso_y_valor_invalido(verify_module):
    """Valida parseo de timestamp ISO y fallback para formato inválido."""

    parsed = verify_module.parse_timestamp("2026-04-05T23:00:00Z")

    assert parsed == datetime(2026, 4, 5, 23, 0, tzinfo=timezone.utc)
    assert verify_module.parse_timestamp("fecha-no-valida") is None


def test_build_dashboard_map_omite_entradas_invalidas(verify_module, monkeypatch):
    """Valida que el mapa de dashboard solo conserve equipos válidos."""

    def fake_fetch_json(url, *, method="GET", payload=None, token="", ca_bundle=""):
        assert url.endswith("/dashboard/resumen")
        assert method == "GET"
        assert token == "token-demo"
        assert payload is None
        assert ca_bundle == ""
        return {
            "equipos": [
                {"id": "1", "ultima_temperatura": 45.0},
                {"id": 2, "ultima_temperatura": 31.2},
                {"id": "bad"},
                "no-es-dict",
            ]
        }

    monkeypatch.setattr(verify_module, "fetch_json", fake_fetch_json)

    dashboard_map = verify_module.build_dashboard_map(
        "http://localhost:8000", "token-demo"
    )

    assert set(dashboard_map.keys()) == {1, 2}


def test_resolve_auth_token_prioriza_variable_entorno(verify_module, monkeypatch):
    """Valida prioridad de VERIFY_ADMIN_TOKEN sobre otras estrategias."""

    monkeypatch.setenv("VERIFY_ADMIN_TOKEN", "env.jwt.token")
    token = verify_module.resolve_auth_token(
        api_url="http://localhost:8000",
        token="",
        email="admin@manttoai.local",
        ca_bundle="",
    )

    assert token == "env.jwt.token"


def test_resolve_auth_token_lee_prompt_si_token_es_dash(verify_module, monkeypatch):
    """Valida lectura de token vía prompt oculto cuando --token es '-'"""

    monkeypatch.delenv("VERIFY_ADMIN_TOKEN", raising=False)
    monkeypatch.setattr(
        verify_module.getpass,
        "getpass",
        lambda prompt="": "prompt.jwt.token",
    )

    token = verify_module.resolve_auth_token(
        api_url="http://localhost:8000",
        token="-",
        email="admin@manttoai.local",
        ca_bundle="",
    )

    assert token == "prompt.jwt.token"


def test_resolve_auth_token_login_fallback_reutiliza_ca_bundle(
    verify_module, monkeypatch
):
    """Valida login fallback y propagación de ca_bundle a fetch_json."""

    captured: dict[str, str] = {}

    def fake_fetch_json(url, *, method="GET", payload=None, token="", ca_bundle=""):
        captured["url"] = url
        captured["method"] = method
        captured["password"] = payload.get("password")
        captured["ca_bundle"] = ca_bundle
        return {"access_token": "login.jwt.token"}

    monkeypatch.delenv("VERIFY_ADMIN_TOKEN", raising=False)
    monkeypatch.setattr(verify_module, "fetch_json", fake_fetch_json)
    monkeypatch.setattr(verify_module, "resolve_auth_password", lambda: "Admin123!")

    token = verify_module.resolve_auth_token(
        api_url="https://api.manttoai.local",
        token="",
        email="admin@manttoai.local",
        ca_bundle="/tmp/ca-bundle.pem",
    )

    assert token == "login.jwt.token"
    assert captured == {
        "url": "https://api.manttoai.local/auth/login",
        "method": "POST",
        "password": "Admin123!",
        "ca_bundle": "/tmp/ca-bundle.pem",
    }


def test_validate_equipo_ok_cuando_lectura_es_reciente(verify_module, monkeypatch):
    """Valida caso OK con lectura reciente y temperatura en dashboard."""

    now = datetime.now(timezone.utc)
    reading_time = now - timedelta(minutes=1)

    def fake_fetch_json(url, *, method="GET", payload=None, token="", ca_bundle=""):
        assert "/lecturas/latest/1" in url
        assert method == "GET"
        assert token == "token-demo"
        assert payload is None
        assert ca_bundle == "/tmp/ca.pem"
        return {
            "timestamp": reading_time.isoformat().replace("+00:00", "Z"),
            "temperatura": 48.2,
        }

    monkeypatch.setattr(verify_module, "fetch_json", fake_fetch_json)

    result = verify_module.validate_equipo(
        api_url="https://api.manttoai.local",
        equipo_id=1,
        dashboard_map={1: {"ultima_temperatura": 48.2}},
        cutoff=now - timedelta(minutes=10),
        token="token-demo",
        ca_bundle="/tmp/ca.pem",
    )

    assert result.lectura_ok is True
    assert result.dashboard_ok is True
    assert result.detalle == "OK"
