"""Tests del router de onboarding."""

from app.models.usuario import Usuario
from app.services.auth_service import create_access_token, hash_password

# ─── helpers ────────────────────────────────────────────────────────────────


def _create_equipo(client, nombre: str = "Equipo Onboarding") -> int:
    """Crea un equipo auxiliar y retorna su id."""

    response = client.post(
        "/equipos",
        json={
            "nombre": nombre,
            "ubicacion": "Laboratorio",
            "tipo": "Motor",
            "estado": "operativo",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _make_visualizador_token(client) -> str:
    """Crea un usuario visualizador en la DB de test y retorna su JWT."""

    session_local = client.app.state.testing_session_local
    with session_local() as db:
        usuario = Usuario(
            nombre="Visualizador Test",
            email="visualizador@manttoai.local",
            password_hash=hash_password("Vis123!"),
            rol="visualizador",
        )
        db.add(usuario)
        db.commit()
    return create_access_token("visualizador@manttoai.local")


# ─── GET /onboarding/status ──────────────────────────────────────────────────


def test_get_status_returns_initial_state(client):
    """Valida que el estado inicial del onboarding sea incompleto con paso 1."""

    response = client.get("/onboarding/status")

    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_completed"] is False
    assert data["onboarding_step"] == 1


def test_get_status_requires_authentication(unauthenticated_client):
    """Valida que el endpoint rechace peticiones sin token."""

    response = unauthenticated_client.get("/onboarding/status")

    assert response.status_code == 401


def test_get_status_rejects_visualizador(client):
    """Valida que el visualizador no pueda acceder al estado del onboarding."""

    token = _make_visualizador_token(client)
    response = client.get(
        "/onboarding/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


# ─── PATCH /onboarding/step ──────────────────────────────────────────────────


def test_update_step_persists_new_step(client):
    """Valida que actualizar el paso lo persista correctamente."""

    response = client.patch("/onboarding/step", json={"step": 3})

    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_step"] == 3
    assert data["onboarding_completed"] is False


def test_update_step_rejects_step_out_of_range(client):
    """Valida que pasos fuera del rango 1-5 sean rechazados."""

    response_low = client.patch("/onboarding/step", json={"step": 0})
    response_high = client.patch("/onboarding/step", json={"step": 6})

    assert response_low.status_code == 422
    assert response_high.status_code == 422


def test_update_step_rejects_when_onboarding_completed(client):
    """Valida que no se pueda avanzar el paso si el onboarding ya está completado."""

    equipo_id = _create_equipo(client)
    client.post("/onboarding/complete", json={"equipo_id": equipo_id})

    response = client.patch("/onboarding/step", json={"step": 2})

    assert response.status_code == 400
    assert "completado" in response.json()["detail"].lower()


# ─── POST /onboarding/complete ───────────────────────────────────────────────


def test_complete_onboarding_with_equipo_marks_completed(client):
    """Valida que completar con equipo real marque onboarding_completed=True."""

    equipo_id = _create_equipo(client)
    response = client.post("/onboarding/complete", json={"equipo_id": equipo_id})

    assert response.status_code == 204

    # El estado debe reflejar que está completado
    status_response = client.get("/onboarding/status")
    assert status_response.json()["onboarding_completed"] is True
    assert status_response.json()["onboarding_step"] is None


def test_complete_onboarding_without_equipo_marks_completed(client):
    """Valida que completar sin equipo (skip) también funcione correctamente."""

    response = client.post("/onboarding/complete", json={})

    assert response.status_code == 204

    status_response = client.get("/onboarding/status")
    assert status_response.json()["onboarding_completed"] is True


def test_complete_onboarding_with_equipo_id_null_marks_completed(client):
    """Valida que equipo_id=null sea aceptado como skip."""

    response = client.post("/onboarding/complete", json={"equipo_id": None})

    assert response.status_code == 204

    status_response = client.get("/onboarding/status")
    assert status_response.json()["onboarding_completed"] is True


def test_complete_onboarding_with_nonexistent_equipo_returns_404(client):
    """Valida que equipo_id inexistente retorne 404."""

    response = client.post("/onboarding/complete", json={"equipo_id": 99999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_reset_onboarding_resets_state(client):
    """Valida que reset reinicia step=1 y completed=False (solo admin)."""

    # Completar onboarding primero
    client.post("/onboarding/complete", json={})

    status_before = client.get("/onboarding/status").json()
    assert status_before["onboarding_completed"] is True

    # Resetear
    response = client.post("/onboarding/reset")
    assert response.status_code == 204

    # Verificar que quedó reseteado
    status_after = client.get("/onboarding/status").json()
    assert status_after["onboarding_completed"] is False
    assert status_after["onboarding_step"] == 1


def test_reset_onboarding_rejects_non_admin(client):
    """Valida que un técnico no pueda resetear el onboarding."""

    token = _make_visualizador_token(client)

    response = client.post(
        "/onboarding/reset",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
