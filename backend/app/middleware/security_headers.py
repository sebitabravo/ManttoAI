"""Middleware que agrega headers de seguridad a cada response."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Agrega headers HTTP de seguridad recomendados por OWASP.

    - HSTS (solo en HTTPS)
    - X-Content-Type-Options
    - X-Frame-Options
    - Referrer-Policy
    - Permissions-Policy
    - Cross-Origin-Opener-Policy
    - Cross-Origin-Resource-Policy
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # X-Content-Type-Options previene MIME sniffing
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # X-Frame-Options previene clickjacking
        response.headers.setdefault("X-Frame-Options", "DENY")

        # Referrer-Policy limita informacion de referrer
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )

        # Permissions-Policy restringe APIs del navegador
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), interest-cohort=()",
        )

        # Cross-Origin isolation headers
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")

        # HSTS solo en HTTPS (no activar en HTTP local)
        if request.url.scheme == "https":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )

        return response
