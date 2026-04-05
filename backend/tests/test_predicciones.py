"""Tests de endpoints de predicciones."""

from app.services import prediccion_service


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye payload válido para crear un equipo."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


def _create_equipo(client, nombre: str = "Equipo Predicciones") -> int:
    """Crea un equipo auxiliar y retorna su id."""

    response = client.post("/equipos", json=_build_equipo_payload(nombre))
    assert response.status_code == 201
    return response.json()["id"]


def _create_lectura(
    client,
    equipo_id: int,
    temperatura: float = 46.0,
    humedad: float = 58.0,
    vib_x: float = 0.35,
    vib_y: float = 0.22,
    vib_z: float = 9.8,
) -> None:
    """Crea una lectura persistida para pruebas de inferencia."""

    response = client.post(
        "/lecturas",
        json={
            "equipo_id": equipo_id,
            "temperatura": temperatura,
            "humedad": humedad,
            "vib_x": vib_x,
            "vib_y": vib_y,
            "vib_z": vib_z,
        },
    )
    assert response.status_code == 201


class _FakeModel:
    """Mock simple de modelo para pruebas de router."""

    def __init__(self, probabilities: list[float]):
        self._probabilities = probabilities

    def predict_proba(self, _rows):
        probability = self._probabilities.pop(0)
        return [[1.0 - probability, probability]]


def _mock_model_loader(probabilities: list[float]):
    """Construye loader mockeado de artefacto para predicciones."""

    model = _FakeModel(list(probabilities))
    return lambda _model_path=None: {
        "model": model,
        "features": ["temperatura", "humedad", "vib_x", "vib_y", "vib_z"],
        "target": "riesgo",
        "model_params": {"n_estimators": 120, "random_state": 42},
    }


def test_post_prediccion_ejecuta_inferencia_real_y_persiste(client, monkeypatch):
    """Valida POST /predicciones/ejecutar/{equipo_id} con inferencia real mockeada."""

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        _mock_model_loader([0.82]),
    )

    equipo_id = _create_equipo(client)
    _create_lectura(client, equipo_id=equipo_id)

    execute_response = client.post(f"/predicciones/ejecutar/{equipo_id}")

    assert execute_response.status_code == 201
    payload = execute_response.json()
    assert payload["equipo_id"] == equipo_id
    assert payload["clasificacion"] == "falla"
    assert payload["probabilidad"] == 0.82

    latest_response = client.get(f"/predicciones/{equipo_id}")
    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == payload["id"]


def test_get_prediccion_devuelve_ultima_persistida(client, monkeypatch):
    """Valida GET /predicciones/{equipo_id} devolviendo la última predicción."""

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        _mock_model_loader([0.45, 0.63]),
    )

    equipo_id = _create_equipo(client)
    _create_lectura(client, equipo_id=equipo_id)

    first = client.post(f"/predicciones/ejecutar/{equipo_id}")
    second = client.post(f"/predicciones/ejecutar/{equipo_id}")

    assert first.status_code == 201
    assert second.status_code == 201

    latest = client.get(f"/predicciones/{equipo_id}")

    assert latest.status_code == 200
    assert latest.json()["id"] == second.json()["id"]
    assert latest.json()["clasificacion"] == "alerta"


def test_post_prediccion_sin_lectura_retorna_404(client, monkeypatch):
    """Valida error cuando no hay lecturas para inferencia."""

    monkeypatch.setattr(
        prediccion_service,
        "load_model_artifact",
        _mock_model_loader([0.7]),
    )

    equipo_id = _create_equipo(client)
    response = client.post(f"/predicciones/ejecutar/{equipo_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Lectura no encontrada para el equipo"


def test_get_prediccion_sin_registros_retorna_404(client):
    """Valida GET /predicciones/{equipo_id} cuando no hay resultados guardados."""

    equipo_id = _create_equipo(client)
    response = client.get(f"/predicciones/{equipo_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Predicción no encontrada para el equipo"
