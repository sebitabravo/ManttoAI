"""Tests de integración para rate limiting diferenciado por rol."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.middleware.rate_limit import limiter
from app.services.auth_service import create_access_token


def _auth_headers(token: str) -> dict[str, str]:
    """Retorna headers con Bearer token para requests autenticados."""

    return {"Authorization": f"Bearer {token}"}


def _create_user_for_test(
    client: TestClient,
    *,
    nombre: str,
    email: str,
    password: str,
    rol: str,
) -> None:
    """Crea un usuario vía API admin para pruebas de límites por rol."""

    response = client.post(
        "/api/v1/usuarios",
        json={
            "nombre": nombre,
            "email": email,
            "password": password,
            "rol": rol,
        },
    )
    assert response.status_code == 201


def _assert_dashboard_limit_for_role(
    client: TestClient,
    *,
    token: str,
    allowed_requests: int,
) -> None:
    """Valida que el rol permita N requests y rechace la siguiente."""

    headers = _auth_headers(token)

    for _ in range(allowed_requests):
        response = client.get("/api/v1/dashboard/resumen", headers=headers)
        assert response.status_code == 200

    blocked_response = client.get("/api/v1/dashboard/resumen", headers=headers)
    assert blocked_response.status_code == 429


@pytest.mark.skip(
    reason="Rate limiting diferenciado por rol no implementado aún en dashboard router"
)
def test_dashboard_resumen_aplica_limites_diferenciados_por_rol(client: TestClient):
    """Debe aplicar cuotas distintas para admin, técnico y visualizador."""

    limiter.reset()

    suffix = uuid4().hex[:8]
    tecnico_email = f"tecnico_rl_{suffix}@manttoai.local"
    visualizador_email = f"visualizador_rl_{suffix}@manttoai.local"

    _create_user_for_test(
        client,
        nombre="Tecnico Rate Limit",
        email=tecnico_email,
        password="Tecnico123!",
        rol="tecnico",
    )
    _create_user_for_test(
        client,
        nombre="Visualizador Rate Limit",
        email=visualizador_email,
        password="Visualizador123!",
        rol="visualizador",
    )

    # Obtener IDs reales de la DB para generar JWTs con subject correcto
    from app.models.usuario import Usuario
    from sqlalchemy import select

    session_local = client.app.state.testing_session_local
    with session_local() as db:
        admin_user = db.scalars(
            select(Usuario).where(Usuario.email == "admin@manttoai.local")
        ).first()
        tecnico_user = db.scalars(
            select(Usuario).where(Usuario.email == tecnico_email)
        ).first()
        visualizador_user = db.scalars(
            select(Usuario).where(Usuario.email == visualizador_email)
        ).first()
        admin_id = admin_user.id
        tecnico_id = tecnico_user.id
        visualizador_id = visualizador_user.id

    admin_token = create_access_token(str(admin_id))
    tecnico_token = create_access_token(str(tecnico_id))
    visualizador_token = create_access_token(str(visualizador_id))

    # visualizador: 3/minute
    _assert_dashboard_limit_for_role(
        client,
        token=visualizador_token,
        allowed_requests=3,
    )

    # técnico: 6/minute
    _assert_dashboard_limit_for_role(
        client,
        token=tecnico_token,
        allowed_requests=6,
    )

    # admin: 10/minute
    _assert_dashboard_limit_for_role(
        client,
        token=admin_token,
        allowed_requests=10,
    )

    limiter.reset()
