"""Tests del asistente de chat híbrido (reglas + fallback Ollama)."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _build_equipo_payload(nombre: str) -> dict:
    """Construye un payload válido para crear un equipo."""
    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


# ---------------------------------------------------------------------------
# Tests del servicio: procesar_mensaje (reglas locales) — síncronos
# ---------------------------------------------------------------------------


class TestProcesarMensajeReglas:
    """Verifica que las palabras clave disparen las respuestas predefinidas."""

    def _run(self, coro):
        """Ejecuta una corrutina de forma síncrona para tests."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_match_keyword_temperatura(self, db):
        """La palabra 'temperatura' devuelve respuesta desde REGLAS_MANTENIMIENTO."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(
            procesar_mensaje("¿Qué significa la temperatura alta?", db)
        )
        assert resultado["fuente"] == "reglas"
        assert (
            "lubricación" in resultado["respuesta"]
            or "temperatura" in resultado["respuesta"].lower()
        )

    def test_match_keyword_vibracion(self, db):
        """La palabra 'vibracion' devuelve respuesta desde REGLAS_MANTENIMIENTO."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(
            procesar_mensaje("tengo una vibracion rara en el motor", db)
        )
        assert resultado["fuente"] == "reglas"
        assert (
            "vibración" in resultado["respuesta"]
            or "desalineación" in resultado["respuesta"]
        )

    def test_match_keyword_alerta(self, db):
        """La palabra 'alerta' dispara la respuesta predefinida."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(procesar_mensaje("qué hago con la alerta?", db))
        assert resultado["fuente"] == "reglas"
        assert (
            "umbral" in resultado["respuesta"]
            or "alerta" in resultado["respuesta"].lower()
        )

    def test_match_keyword_dashboard(self, db):
        """La palabra 'dashboard' devuelve la descripción del panel."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(procesar_mensaje("para qué sirve el dashboard?", db))
        assert resultado["fuente"] == "reglas"
        assert (
            "dashboard" in resultado["respuesta"].lower()
            or "estado general" in resultado["respuesta"].lower()
        )

    def test_match_keyword_mantenimiento(self, db):
        """La palabra 'mantenimiento' dispara la respuesta sobre mantenimiento preventivo."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(
            procesar_mensaje("hablame del mantenimiento preventivo", db)
        )
        assert resultado["fuente"] == "reglas"

    def test_match_keyword_bomba(self, db):
        """La palabra 'bomba' devuelve la respuesta sobre bombas centrífugas."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(procesar_mensaje("tengo un problema con la bomba", db))
        assert resultado["fuente"] == "reglas"
        assert (
            "cavitación" in resultado["respuesta"]
            or "bomba" in resultado["respuesta"].lower()
        )

    def test_match_keyword_probabilidad(self, db):
        """La palabra 'probabilidad' dispara la respuesta sobre niveles de riesgo."""
        from app.services.chat_service import procesar_mensaje

        resultado = self._run(
            procesar_mensaje("qué significa la probabilidad de falla?", db)
        )
        assert resultado["fuente"] == "reglas"
        assert (
            "riesgo" in resultado["respuesta"].lower() or "0" in resultado["respuesta"]
        )

    def test_mensaje_sin_keyword_cae_a_fallback(self, db):
        """Un mensaje sin palabras clave va al fallback cuando Ollama falla."""
        from app.services.chat_service import procesar_mensaje

        with patch(
            "app.services.chat_service.consultar_ollama",
            new_callable=AsyncMock,
            side_effect=Exception("Ollama no disponible en test"),
        ):
            resultado = self._run(procesar_mensaje("xyznokeywordabc defghi", db))
            assert resultado["fuente"] == "fallback"
            assert "no está disponible" in resultado["respuesta"]

    def test_mensaje_sin_keyword_ollama_ok(self, db):
        """Un mensaje sin keywords usa Ollama cuando está disponible."""
        from app.services.chat_service import procesar_mensaje

        with patch(
            "app.services.chat_service.consultar_ollama",
            new_callable=AsyncMock,
            return_value="Revisa los rodamientos del equipo.",
        ):
            resultado = self._run(procesar_mensaje("xyznokeywordabc defghi", db))
            assert resultado["fuente"] == "ollama"
            assert "rodamientos" in resultado["respuesta"]


# ---------------------------------------------------------------------------
# Tests del servicio: consultar_ollama (con mocks)
# ---------------------------------------------------------------------------


class TestConsultarOllama:
    """Verifica la integración con Ollama usando mocks de httpx."""

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_consultar_ollama_exitoso(self, db):
        """Ollama devuelve una respuesta válida."""
        from app.services.chat_service import consultar_ollama

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "Revisa los rodamientos del motor."
        }
        mock_response.raise_for_status = MagicMock()

        with patch(
            "app.services.chat_service.get_dashboard_summary",
            return_value={
                "total_equipos": 3,
                "alertas_activas": 1,
                "equipos_en_riesgo": 0,
                "equipos": [],
            },
        ):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                resultado = self._run(consultar_ollama("¿Qué hago?", db))
                assert "rodamientos" in resultado

    def test_consultar_ollama_timeout(self, db):
        """Ollama lanza TimeoutException y se propaga."""
        import httpx
        from app.services.chat_service import consultar_ollama

        with patch(
            "app.services.chat_service.get_dashboard_summary",
            return_value={
                "total_equipos": 0,
                "alertas_activas": 0,
                "equipos_en_riesgo": 0,
                "equipos": [],
            },
        ):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(
                    side_effect=httpx.TimeoutException("timeout")
                )
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                with pytest.raises(httpx.TimeoutException):
                    self._run(consultar_ollama("¿algo?", db))

    def test_consultar_ollama_http_error(self, db):
        """Ollama devuelve error HTTP y se propaga."""
        import httpx
        from app.services.chat_service import consultar_ollama

        # Construir un mock de Response con los atributos que usa el handler
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        error = httpx.HTTPStatusError(
            "Server Error '500'",
            request=MagicMock(),
            response=mock_response,
        )

        with patch(
            "app.services.chat_service.get_dashboard_summary",
            return_value={
                "total_equipos": 0,
                "alertas_activas": 0,
                "equipos_en_riesgo": 0,
                "equipos": [],
            },
        ):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(side_effect=error)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                with pytest.raises(httpx.HTTPStatusError):
                    self._run(consultar_ollama("test", db))

    def test_consultar_ollama_context_error_falls_back(self, db):
        """Si get_dashboard_summary falla, usa contexto genérico."""
        from app.services.chat_service import consultar_ollama

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Respuesta genérica."}
        mock_response.raise_for_status = MagicMock()

        with patch(
            "app.services.chat_service.get_dashboard_summary",
            side_effect=Exception("DB error"),
        ):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                resultado = self._run(consultar_ollama("pregunta", db))
                assert resultado == "Respuesta genérica."

    def test_consultar_ollama_con_equipos_en_contexto(self, db):
        """Ollama recibe contexto con equipos detallados."""
        from app.services.chat_service import consultar_ollama

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "El motor está en riesgo."}
        mock_response.raise_for_status = MagicMock()

        summary = {
            "total_equipos": 2,
            "alertas_activas": 1,
            "equipos_en_riesgo": 1,
            "equipos": [
                {
                    "id": 1,
                    "nombre": "Motor A",
                    "alertas_activas": 1,
                    "ultima_probabilidad": 0.85,
                    "ultima_temperatura": 78.5,
                },
                {
                    "id": 2,
                    "nombre": "Bomba B",
                    "alertas_activas": 0,
                    "ultima_probabilidad": None,
                    "ultima_temperatura": None,
                },
            ],
        }

        with patch(
            "app.services.chat_service.get_dashboard_summary", return_value=summary
        ):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                resultado = self._run(consultar_ollama("estado de la planta?", db))
                assert "riesgo" in resultado.lower() or "motor" in resultado.lower()

    def test_consultar_ollama_error_inesperado(self, db):
        """Error genérico al consultar Ollama se propaga."""
        from app.services.chat_service import consultar_ollama

        with patch(
            "app.services.chat_service.get_dashboard_summary",
            return_value={
                "total_equipos": 0,
                "alertas_activas": 0,
                "equipos_en_riesgo": 0,
                "equipos": [],
            },
        ):
            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(side_effect=ConnectionError("red caída"))
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                with pytest.raises(ConnectionError):
                    self._run(consultar_ollama("test", db))


# ---------------------------------------------------------------------------
# Tests del router: POST /chat
# ---------------------------------------------------------------------------


class TestChatRouter:
    """Tests de los endpoints del router de chat."""

    def test_chat_con_keyword_retorna_respuesta_reglas(self, client):
        """POST /chat con keyword conocido devuelve fuente 'reglas'."""
        payload = {"mensaje": "tengo una alerta activa"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["fuente"] == "reglas"
        assert "respuesta" in data

    def test_chat_persiste_historial(self, client):
        """POST /chat guarda el mensaje en la tabla mensajes_chat."""
        payload = {"mensaje": "hablame de la vibración del equipo"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 200

        # Verificar que se puede obtener el historial
        hist_response = client.get("/chat/historial")
        assert hist_response.status_code == 200
        historial = hist_response.json()
        assert len(historial) >= 1
        assert historial[0]["mensaje_usuario"] == "hablame de la vibración del equipo"
        assert historial[0]["fuente"] == "reglas"

    def test_chat_requiere_autenticacion(self, unauthenticated_client):
        """POST /chat rechaza si no hay token."""
        payload = {"mensaje": "temperatura alta"}
        response = unauthenticated_client.post("/chat", json=payload)
        assert response.status_code in (401, 403)

    def test_chat_mensaje_muy_corto(self, client):
        """POST /chat rechaza mensajes con menos de 2 caracteres."""
        payload = {"mensaje": "x"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 422

    def test_chat_mensaje_muy_largo(self, client):
        """POST /chat rechaza mensajes con más de 500 caracteres."""
        payload = {"mensaje": "a" * 501}
        response = client.post("/chat", json=payload)
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests del router: GET /chat/historial
# ---------------------------------------------------------------------------


class TestChatHistorial:
    """Tests del endpoint de historial de chat."""

    def test_historial_vacio_retorna_lista_vacia(self, client):
        """GET /chat/historial sin mensajes retorna lista vacía."""
        response = client.get("/chat/historial")
        assert response.status_code == 200
        assert response.json() == []

    def test_historial_requiere_admin(self, client):
        """GET /chat/historial está disponible para admin (el client fixture es admin)."""
        response = client.get("/chat/historial")
        assert response.status_code == 200

    def test_historial_respeta_paginacion(self, client):
        """GET /chat/historial con skip/limit funciona correctamente."""
        # Crear algunos mensajes
        for i in range(3):
            client.post("/chat", json={"mensaje": f"pregunta sobre temperatura {i}"})

        # Pedir solo 2
        response = client.get("/chat/historial?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# Tests del router: GET /chat/dataset-export
# ---------------------------------------------------------------------------


class TestChatDatasetExport:
    """Tests del endpoint de exportación de dataset para fine-tuning."""

    def test_dataset_export_sin_mensajes(self, client):
        """GET /chat/dataset-export retorna vacío si no hay mensajes."""
        response = client.get("/chat/dataset-export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-ndjson"

    def test_dataset_export_con_mensajes(self, client):
        """GET /chat/dataset-export retorna JSONL válido con mensajes previos."""
        # Crear un mensaje primero
        client.post("/chat", json={"mensaje": "qué es la temperatura alta?"})

        response = client.get("/chat/dataset-export")
        assert response.status_code == 200
        content = response.text
        assert "system" in content
        assert "user" in content
        assert "assistant" in content

    def test_dataset_export_requiere_admin(self, unauthenticated_client):
        """GET /chat/dataset-export rechaza sin autenticación."""
        response = unauthenticated_client.get("/chat/dataset-export")
        assert response.status_code in (401, 403)
