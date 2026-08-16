"""Regresiones del despliegue Render Free sin comandos de pre-deploy pagos."""

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def test_render_free_blueprint_no_declara_predeploy_pago():
    """El blueprint Free no debe usar una capacidad exclusiva de planes pagos."""

    source = (ROOT_DIR / "render.yaml").read_text(encoding="utf-8")

    assert "plan: free" in source
    assert "preDeployCommand" not in source


def test_render_docker_seed_antes_de_iniciar_uvicorn():
    """El contenedor Free debe sembrar la demo antes de aceptar tráfico."""

    source = (ROOT_DIR / "backend" / "Dockerfile.render").read_text(encoding="utf-8")

    assert "python /app/seed_db.py" in source
    assert "exec uvicorn app.main:app" in source


def test_render_configura_retencion_de_telemetria_para_aiven_free():
    """El blueprint debe limitar el crecimiento de lecturas en Aiven Free."""

    source = (ROOT_DIR / "render.yaml").read_text(encoding="utf-8")

    assert "key: TELEMETRY_RETENTION_DAYS" in source
    assert 'value: "30"' in source


def test_backend_docker_context_excluye_env_runtime():
    """El contexto Compose no debe copiar secretos locales a la imagen."""

    source = (ROOT_DIR / "backend" / ".dockerignore").read_text(encoding="utf-8")

    assert ".env" in source.splitlines()
    assert ".env.*" in source.splitlines()


def test_frontend_docker_context_excluye_env_runtime():
    """El build Vite tampoco debe recibir secretos locales como contexto."""

    source = (ROOT_DIR / "frontend" / ".dockerignore").read_text(encoding="utf-8")

    assert ".env" in source.splitlines()
    assert ".env.*" in source.splitlines()


def test_vercel_configura_build_vite_y_salida_estatica():
    """La configuración local debe imponerse a presets Vercel ajenos."""
    source = (ROOT_DIR / "frontend" / "vercel.json").read_text(encoding="utf-8")
    config = json.loads(source)

    assert config["framework"] == "vite"
    assert config["installCommand"] == "npm ci"
    assert config["buildCommand"] == "npm run build"
    assert config["outputDirectory"] == "dist"
