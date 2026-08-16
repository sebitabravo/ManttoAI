"""Pruebas de resolución segura de IP para rate limiting."""

from types import SimpleNamespace

from starlette.requests import Request

from app.middleware import rate_limit


def _request(peer: str, forwarded: str | None = None) -> Request:
    """Construye una request ASGI mínima con peer y X-Forwarded-For."""

    headers = []
    if forwarded is not None:
        headers.append((b"x-forwarded-for", forwarded.encode("ascii")))

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": (peer, 1234),
        "server": ("localhost", 8000),
        "scheme": "http",
    }
    return Request(scope)


def test_get_real_ip_does_not_trust_forwarded_header_from_unknown_peer():
    """Un cliente no puede rotar X-Forwarded-For para obtener buckets nuevos."""

    request = _request("198.51.100.20", "203.0.113.10")

    assert rate_limit.get_real_ip(request) == "198.51.100.20"


def test_get_real_ip_uses_first_untrusted_forwarded_hop_for_trusted_proxy(
    monkeypatch,
):
    """El header solo se procesa cuando el peer pertenece a un proxy confiable."""

    monkeypatch.setattr(
        rate_limit,
        "get_settings",
        lambda: SimpleNamespace(trusted_proxy_ips="10.0.0.0/8"),
    )
    request = _request("10.0.0.5", "203.0.113.10, 10.0.0.5")

    assert rate_limit.get_real_ip(request) == "203.0.113.10"
