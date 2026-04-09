"""Tests de exportación de reportes CSV/PDF."""

from fastapi.testclient import TestClient

from app.services.report_service import _build_simple_pdf


def _create_equipo(client: TestClient, nombre: str = "Equipo Reporte") -> dict:
    """Crea un equipo de apoyo para tests de reportes."""

    response = client.post(
        "/api/v1/equipos",
        json={
            "nombre": nombre,
            "ubicacion": "Lab QA",
            "tipo": "Motor",
            "descripcion": "Equipo para pruebas de reportes",
            "estado": "operativo",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_export_lecturas_csv_incluye_header_y_datos(client: TestClient):
    """Debe exportar lecturas en CSV con attachment y filas."""

    equipo = _create_equipo(client, nombre="Equipo CSV Lecturas")

    lectura_response = client.post(
        "/api/v1/lecturas",
        json={
            "equipo_id": equipo["id"],
            "temperatura": 45.2,
            "humedad": 60.0,
            "vib_x": 0.3,
            "vib_y": 0.2,
            "vib_z": 9.8,
        },
    )
    assert lectura_response.status_code == 201

    response = client.get("/api/v1/reportes/lecturas.csv?limit=10")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment;" in response.headers["content-disposition"]
    assert "manttoai_lecturas" in response.headers["content-disposition"]
    assert "filename*=UTF-8''" in response.headers["content-disposition"]

    csv_text = response.text.lstrip("\ufeff")
    assert "equipo_nombre" in csv_text
    assert "Equipo CSV Lecturas" in csv_text


def test_export_alertas_csv_incluye_columnas_aun_sin_datos(client: TestClient):
    """Debe devolver cabecera CSV de alertas aunque no existan filas."""

    response = client.get("/api/v1/reportes/alertas.csv?limit=10")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "manttoai_alertas" in response.headers["content-disposition"]

    csv_text = response.text.lstrip("\ufeff")
    header = csv_text.splitlines()[0]
    assert "equipo_nombre" in header
    assert "email_enviado" in header


def test_export_mantenciones_csv_incluye_registros(client: TestClient):
    """Debe exportar mantenciones con datos del equipo asociado."""

    equipo = _create_equipo(client, nombre="Equipo CSV Mantenciones")

    mantencion_response = client.post(
        "/api/v1/mantenciones",
        json={
            "equipo_id": equipo["id"],
            "tipo": "preventiva",
            "descripcion": "Cambio de filtro",
            "estado": "programada",
        },
    )
    assert mantencion_response.status_code == 201

    response = client.get("/api/v1/reportes/mantenciones.csv?limit=10")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "manttoai_mantenciones" in response.headers["content-disposition"]

    csv_text = response.text.lstrip("\ufeff")
    assert "Cambio de filtro" in csv_text
    assert "Equipo CSV Mantenciones" in csv_text


def test_export_informe_ejecutivo_pdf_devuelve_pdf_valido(client: TestClient):
    """Debe generar informe ejecutivo en PDF descargable."""

    response = client.get("/api/v1/reportes/ejecutivo.pdf")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "manttoai_informe_ejecutivo" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_export_reportes_requiere_autenticacion(unauthenticated_client: TestClient):
    """Endpoints de reportes deben rechazar requests sin auth."""

    response = unauthenticated_client.get("/api/v1/reportes/lecturas.csv")
    assert response.status_code == 401


def test_export_lecturas_csv_sanitiza_formulas_en_campos_texto(client: TestClient):
    """Debe proteger CSV contra inyección de fórmulas en nombres de equipo."""

    equipo = _create_equipo(client, nombre='=HYPERLINK("http://malicioso")')

    lectura_response = client.post(
        "/api/v1/lecturas",
        json={
            "equipo_id": equipo["id"],
            "temperatura": 30.0,
            "humedad": 55.0,
            "vib_x": 0.1,
            "vib_y": 0.1,
            "vib_z": 0.1,
        },
    )
    assert lectura_response.status_code == 201

    response = client.get("/api/v1/reportes/lecturas.csv?limit=10")
    assert response.status_code == 200

    csv_text = response.text.lstrip("\ufeff")
    assert "'=HYPERLINK" in csv_text


def test_export_reportes_valida_timezone_mixta_en_rango(client: TestClient):
    """Debe retornar 400 cuando se mezclan datetimes naive y aware."""

    response = client.get(
        "/api/v1/reportes/lecturas.csv",
        params={
            "desde": "2026-04-08T10:00:00",
            "hasta": "2026-04-08T11:00:00Z",
        },
    )

    assert response.status_code == 400
    assert "zona horaria" in response.json()["detail"].lower()


def test_export_csv_sanitiza_formulas_con_caracteres_invisibles(client: TestClient):
    """Debe sanitizar fórmulas aunque haya marcadores invisibles al inicio."""

    equipo = _create_equipo(client, nombre="\u200e=SUM(1,2)")

    lectura_response = client.post(
        "/api/v1/lecturas",
        json={
            "equipo_id": equipo["id"],
            "temperatura": 33.0,
            "humedad": 58.0,
            "vib_x": 0.2,
            "vib_y": 0.2,
            "vib_z": 0.2,
        },
    )
    assert lectura_response.status_code == 201

    response = client.get("/api/v1/reportes/lecturas.csv?limit=10")
    assert response.status_code == 200

    csv_text = response.text.lstrip("\ufeff")
    assert "'\u200e=SUM(1,2)" in csv_text


def test_build_simple_pdf_agrega_aviso_si_excede_limite_lineas() -> None:
    """Debe advertir truncamiento cuando el contenido supera una página."""

    lines = [f"Linea {index} con contenido de prueba" for index in range(80)]
    pdf_content = _build_simple_pdf(lines)

    assert b"AVISO" in pdf_content
