"""Tests unitarios para métricas con Redis + fallback en memoria."""

import asyncio

import pytest

from app.routers import metrics


def teardown_function() -> None:
    """Limpia estado global de métricas entre tests."""

    metrics._mem_request_count.clear()
    metrics._mem_request_duration.clear()


def test_track_request_metrics_acota_historial_de_duraciones() -> None:
    """Debe mantener buffer acotado para evitar crecimiento infinito."""

    endpoint = "unit_test_endpoint"

    @metrics.track_request_metrics(endpoint)
    async def _fake_handler() -> dict[str, str]:
        return {"status": "ok"}

    total_calls = metrics._MAX_DURATION_SAMPLES + 25
    for _ in range(total_calls):
        asyncio.run(_fake_handler())

    # Verificar usando las funciones publicas (Redis-aware)
    counts = metrics._get_all_counts()
    assert counts.get(endpoint) == total_calls

    # Verificar que el buffer en memoria esta acotado
    # (Redis puede no estar disponible en tests, asi que verificamos el fallback)
    if endpoint in metrics._mem_request_duration:
        assert len(metrics._mem_request_duration[endpoint]) == metrics._MAX_DURATION_SAMPLES


def test_get_average_duration_considera_ultimos_n_registros() -> None:
    """Debe calcular promedio sobre los últimos N registros."""

    endpoint = "unit_test_average"
    metrics._mem_request_duration[endpoint] = metrics.deque(
        [0.1, 0.2, 0.3, 0.4],
        maxlen=metrics._MAX_DURATION_SAMPLES,
    )

    average = metrics._get_average_duration(endpoint, last_n=2)
    # Debe promediar los ultimos 2 valores: (0.3 + 0.4) / 2 = 0.35
    assert average == pytest.approx(0.35)
