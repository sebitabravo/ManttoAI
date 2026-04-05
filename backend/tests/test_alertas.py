"""Tests de alertas."""


def test_list_alertas_returns_array(client):
    """Valida que el endpoint retorne un arreglo."""

    response = client.get("/alertas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_mark_alert_as_read(client):
    """Valida el marcado de una alerta demo."""

    response = client.patch("/alertas/1/leer")
    assert response.status_code == 200
    assert response.json()["leida"] is True
