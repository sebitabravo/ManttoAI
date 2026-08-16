"""Regresiones del seed de equipos demo y el contrato MQTT por MAC."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_seed_module():
    """Carga el script de seed sin ejecutarlo."""

    script_path = Path(__file__).resolve().parents[2] / "scripts" / "seed_db.py"
    spec = importlib.util.spec_from_file_location("manttoai_seed_db_test", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_seed_equipos_asigna_mac_a_equipos_demo(db):
    """El seed debe dejar una MAC persistida para que MQTT pueda resolverla."""

    seed_module = _load_seed_module()

    equipos, created_count, _updated_count = seed_module.seed_equipos(db)

    assert created_count == len(seed_module.EQUIPOS_DEMO)
    assert [equipo.mac_address for equipo in equipos] == [
        "02:00:00:00:00:01",
        "02:00:00:00:00:02",
        "02:00:00:00:00:03",
        "02:00:00:00:00:04",
        "02:00:00:00:00:05",
        "02:00:00:00:00:06",
    ]
