"""Regresiones del script de prueba de carga."""

import asyncio

import load_test


def test_simulate_concurrent_users_respects_requests_per_user(monkeypatch):
    """Cada usuario debe generar exactamente la cantidad configurada de requests."""

    calls: list[tuple[str, str]] = []

    async def fake_make_request(_session, method, url, token=None):
        calls.append((method, url))
        return True, 1.0, 200

    monkeypatch.setattr(load_test, "make_request", fake_make_request)

    results = asyncio.run(
        load_test.simulate_concurrent_users(
            base_url="http://testserver",
            num_users=3,
            requests_per_user=4,
        )
    )

    assert len(calls) == 12
    assert sum(result.total_requests for result in results.values()) == 12
    assert all(result.failed_requests == 0 for result in results.values())
