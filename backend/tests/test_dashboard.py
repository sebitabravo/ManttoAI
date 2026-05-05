"""Tests del contrato de resumen para dashboard."""

import pytest

from app.services import prediccion_service


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye payload válido para crear un equipo."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "rubro": "industrial",
        "estado": "operativo",
    }


def _create_equipo(client, nombre: str) -> int:
    """Crea equipo auxiliar y retorna su id."""

    response = client.post("/equipos", json=_build_equipo_payload(nombre))
    assert response.status_code == 201
    return response.json()["id"]


def _create_umbral(
    client,
    equipo_id: int,
    variable: str,
    valor_min: float,
    valor_max: float,
) -> None:
    """Crea umbral para forzar o evitar alertas según cada equipo."""

    response = client.post(
        "/umbrales",
        json={
            "equipo_id": equipo_id,
            "variable": variable,
            "valor_min": valor_min,
            "valor_max": valor_max,
        },
    )
    assert response.status_code == 201


def _create_lectura(client, equipo_id: int, temperatura: float) -> None:
    """Crea lectura persistida para dashboard y predicciones."""

    response = client.post(
        "/lecturas",
        json={
            "equipo_id": equipo_id,
            "temperatura": temperatura,
            "humedad": 58.0,
            "vib_x": 0.35,
            "vib_y": 0.22,
            "vib_z": 9.8,
        },
    )
    assert response.status_code == 201


class _FakeModel:
    """Mock de modelo para devolver probabilidades controladas."""

    def __init__(self, probabilities: list[float]):
        self._probabilities = list(probabilities)

    def predict_proba(self, _rows):
        probability = self._probabilities.pop(0)
        return [[1.0 - probability, probability]]


def _mock_model_loader(probabilities: list[float]):
    """Crea loader mockeado de artefacto ML para tests de dashboard."""

    model = _FakeModel(probabilities)
    return lambda _model_path=None: {
        "model": model,
        "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
        "target": "riesgo",
        "model_params": {"n_estimators": 120, "random_state": 42},
    }


def test_dashboard_summary_returns_compact_contract_without_data(client):
    """Valida contrato estable y compacto cuando no existen registros."""

    response = client.get("/dashboard/resumen")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {
        "total_equipos",
        "alertas_activas",
        "equipos_en_riesgo",
        "ultima_clasificacion",
        "probabilidad_falla",
        "equipos",
    }
    assert payload == {
        "total_equipos": 0,
        "alertas_activas": 0,
        "equipos_en_riesgo": 0,
        "ultima_clasificacion": "normal",
        "probabilidad_falla": 0.0,
        "equipos": [],
    }


def test_dashboard_summary_returns_real_data_for_polling(client, monkeypatch):
    """Valida resumen real con equipos, alertas, lectura y predicción."""

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        _mock_model_loader([0.22, 0.45, 0.68]),
    )

    equipo_principal_id = _create_equipo(client, "Compresor principal")
    equipo_respaldo_id = _create_equipo(client, "Bomba respaldo")

    _create_umbral(
        client,
        equipo_id=equipo_principal_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=40.0,
    )
    _create_umbral(
        client,
        equipo_id=equipo_respaldo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=60.0,
    )

    _create_lectura(client, equipo_id=equipo_principal_id, temperatura=48.0)
    _create_lectura(client, equipo_id=equipo_principal_id, temperatura=51.2)
    _create_lectura(client, equipo_id=equipo_respaldo_id, temperatura=35.4)

    assert (
        client.post(f"/predicciones/ejecutar/{equipo_respaldo_id}").status_code == 201
    )
    assert (
        client.post(f"/predicciones/ejecutar/{equipo_principal_id}").status_code == 201
    )
    assert (
        client.post(f"/predicciones/ejecutar/{equipo_principal_id}").status_code == 201
    )

    response = client.get("/dashboard/resumen")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {
        "total_equipos",
        "alertas_activas",
        "equipos_en_riesgo",
        "ultima_clasificacion",
        "probabilidad_falla",
        "equipos",
    }
    assert payload["total_equipos"] == 2
    assert payload["alertas_activas"] == 1
    assert payload["equipos_en_riesgo"] == 1
    assert payload["ultima_clasificacion"] == "alerta"
    assert payload["probabilidad_falla"] == pytest.approx(0.68, abs=1e-6)

    equipos = payload["equipos"]
    assert len(equipos) == 2
    assert all(
        set(equipo.keys())
        == {
            "id",
            "nombre",
            "rubro",
            "ultima_temperatura",
            "ultima_probabilidad",
            # Campo agregado para el indicador visual de predicción en el frontend
            "ultima_clasificacion",
            "alertas_activas",
        }
        for equipo in equipos
    )

    equipos_por_id = {equipo["id"]: equipo for equipo in equipos}

    principal = equipos_por_id[equipo_principal_id]
    assert principal["nombre"] == "Compresor principal"
    assert principal["rubro"] == "industrial"
    assert principal["ultima_temperatura"] == pytest.approx(51.2, abs=1e-6)
    assert principal["ultima_probabilidad"] == pytest.approx(0.68, abs=1e-6)
    assert principal["alertas_activas"] == 1

    respaldo = equipos_por_id[equipo_respaldo_id]
    assert respaldo["nombre"] == "Bomba respaldo"
    assert respaldo["rubro"] == "industrial"
    assert respaldo["ultima_temperatura"] == pytest.approx(35.4, abs=1e-6)
    assert respaldo["ultima_probabilidad"] == pytest.approx(0.22, abs=1e-6)
    assert respaldo["alertas_activas"] == 0
