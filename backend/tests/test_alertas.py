"""Tests de alertas."""

from contextlib import contextmanager

from sqlalchemy.exc import OperationalError

from app.services import alerta_service
from app.services import email_service


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye un payload válido para crear equipos."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


def _create_equipo(client, nombre: str = "Equipo Alertas") -> int:
    """Crea un equipo auxiliar y retorna su id."""

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
    """Crea un umbral para el equipo indicado."""

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


def _create_lectura(
    client,
    equipo_id: int,
    temperatura: float = 40.0,
    humedad: float = 55.0,
    vib_x: float = 0.3,
    vib_y: float = 0.2,
    vib_z: float = 9.8,
) -> None:
    """Crea una lectura para gatillar evaluación de umbrales."""

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


def test_breach_temperatura_creates_persisted_alert(client):
    """Valida que una temperatura fuera de rango cree alerta persistida."""

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=45.0,
    )

    _create_lectura(client, equipo_id=equipo_id, temperatura=58.0)

    response = client.get("/alertas", params={"equipo_id": equipo_id})

    assert response.status_code == 200
    alertas = response.json()
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "temperatura"
    assert alertas[0]["leida"] is False


def test_critical_alert_marks_email_enviado_when_send_succeeds(client, monkeypatch):
    """Valida que una alerta crítica marque email_enviado=True al enviar."""

    calls: list[tuple[str, str]] = []

    class FakeSMTPClient:
        """Mock de cliente SMTP que registra llamadas."""

        def send_message(self, message):
            calls.append((message["Subject"], message["To"]))

    @contextmanager
    def fake_get_smtp_client():
        yield FakeSMTPClient()

    monkeypatch.setattr(email_service, "get_smtp_client", fake_get_smtp_client)
    monkeypatch.setattr(alerta_service, "get_smtp_client", fake_get_smtp_client)

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=45.0,
    )

    _create_lectura(client, equipo_id=equipo_id, temperatura=57.0)

    response = client.get("/alertas", params={"equipo_id": equipo_id})
    assert response.status_code == 200

    alertas = response.json()
    assert len(alertas) == 1
    assert alertas[0]["email_enviado"] is True
    assert len(calls) == 1


def test_critical_alert_marks_email_enviado_false_when_send_fails(
    client,
    monkeypatch,
):
    """Valida que el fallo de envío deje email_enviado=False."""

    @contextmanager
    def fake_get_smtp_client_failing():
        raise RuntimeError("smtp unavailable")
        yield  # noqa: unreachable — necesario para que sea generator

    monkeypatch.setattr(email_service, "get_smtp_client", fake_get_smtp_client_failing)
    monkeypatch.setattr(alerta_service, "get_smtp_client", fake_get_smtp_client_failing)

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=45.0,
    )

    _create_lectura(client, equipo_id=equipo_id, temperatura=58.5)

    response = client.get("/alertas", params={"equipo_id": equipo_id})
    assert response.status_code == 200

    alertas = response.json()
    assert len(alertas) == 1
    assert alertas[0]["email_enviado"] is False


def test_repeated_breach_does_not_duplicate_active_alert(client):
    """Valida que no se duplique alerta activa por breach repetido."""

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=45.0,
    )

    _create_lectura(client, equipo_id=equipo_id, temperatura=57.0)
    _create_lectura(client, equipo_id=equipo_id, temperatura=59.0)

    response = client.get(
        "/alertas",
        params={"equipo_id": equipo_id, "solo_no_leidas": True},
    )

    assert response.status_code == 200
    alertas = response.json()
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "temperatura"


def test_normal_reading_does_not_create_new_alert(client):
    """Valida que una lectura normal no cree alertas innecesarias."""

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=70.0,
    )

    _create_lectura(client, equipo_id=equipo_id, temperatura=42.0)

    response = client.get("/alertas", params={"equipo_id": equipo_id})

    assert response.status_code == 200
    assert response.json() == []


def test_lock_equipo_alert_scope_ignores_unsupported_for_update():
    """Valida fallback seguro cuando el motor no soporta FOR UPDATE."""

    class _FailingSession:
        def execute(self, _statement):
            raise OperationalError("SELECT 1", {}, Exception("for update unsupported"))

    alerta_service._lock_equipo_alert_scope(_FailingSession(), equipo_id=1)


def test_breach_vibracion_creates_persisted_alert(client):
    """Valida que una vibración fuera de rango cree alerta persistida."""

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="vib_x",
        valor_min=0.0,
        valor_max=0.5,
    )

    _create_lectura(client, equipo_id=equipo_id, vib_x=0.9)

    response = client.get("/alertas", params={"equipo_id": equipo_id})

    assert response.status_code == 200
    alertas = response.json()
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "vibracion"


def test_patch_alerta_marks_record_as_read(client):
    """Valida que PATCH /alertas/{id}/leer actualice datos persistidos."""

    equipo_id = _create_equipo(client)
    _create_umbral(
        client,
        equipo_id=equipo_id,
        variable="temperatura",
        valor_min=10.0,
        valor_max=45.0,
    )
    _create_lectura(client, equipo_id=equipo_id, temperatura=59.0)

    initial = client.get(
        "/alertas",
        params={"equipo_id": equipo_id, "solo_no_leidas": True},
    )
    assert initial.status_code == 200
    alertas_no_leidas = initial.json()
    assert len(alertas_no_leidas) == 1
    alerta_id = alertas_no_leidas[0]["id"]

    patch_response = client.patch(f"/alertas/{alerta_id}/leer")
    assert patch_response.status_code == 200
    assert patch_response.json()["id"] == alerta_id
    assert patch_response.json()["leida"] is True

    after_patch = client.get(
        "/alertas",
        params={"equipo_id": equipo_id, "solo_no_leidas": True},
    )
    assert after_patch.status_code == 200
    assert after_patch.json() == []
