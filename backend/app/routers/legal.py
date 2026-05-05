"""Endpoints para servir documentación legal."""

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/legal", tags=["legal"])

# Directorio base de archivos legales (backend/static/legal)
LEGAL_DIR = Path(__file__).resolve().parents[2] / "static" / "legal"


@router.get("/terms-of-service")
async def get_terms_of_service():
    """Retorna los Términos de Servicio."""

    file_path = LEGAL_DIR / "terms-of-service.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/privacy-policy")
async def get_privacy_policy():
    """Retorna la Política de Privacidad."""

    file_path = LEGAL_DIR / "privacy-policy.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/dpa")
async def get_dpa():
    """Retorna el Data Processing Agreement (DPA)."""

    file_path = LEGAL_DIR / "dpa.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
