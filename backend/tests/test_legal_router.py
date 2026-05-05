"""Tests de endpoints públicos de documentación legal."""


def test_terms_of_service_endpoint_returns_legal_document(unauthenticated_client):
    """Valida que Términos de Servicio esté disponible en JSON."""

    response = unauthenticated_client.get("/legal/terms-of-service")

    assert response.status_code == 200
    data = response.json()
    assert data["title"].startswith("Términos de Servicio")
    assert isinstance(data["sections"], list)
    assert len(data["sections"]) > 0


def test_privacy_policy_endpoint_returns_legal_document(unauthenticated_client):
    """Valida que Política de Privacidad esté disponible en JSON."""

    response = unauthenticated_client.get("/legal/privacy-policy")

    assert response.status_code == 200
    data = response.json()
    assert data["title"].startswith("Política de Privacidad")
    assert isinstance(data["sections"], list)
    assert len(data["sections"]) > 0


def test_dpa_endpoint_returns_legal_document(unauthenticated_client):
    """Valida que DPA esté disponible en JSON."""

    response = unauthenticated_client.get("/legal/dpa")

    assert response.status_code == 200
    data = response.json()
    assert data["title"].startswith("Data Processing Agreement")
    assert isinstance(data["sections"], list)
    assert len(data["sections"]) > 0
