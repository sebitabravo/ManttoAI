"""Tests del servicio de SLA (Service Level Agreement) — uptime, downtime y reportes mensuales."""

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.models.sla import SLAEvent
from app.services import sla_service


def _create_org(db, nombre: str = "Org SLA", slug: str = "org-sla") -> int:
    """Crea una organizacion auxiliar y retorna su id."""

    from app.models.organizacion import Organizacion

    org = Organizacion(nombre=nombre, slug=slug)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org.id


def test_calculate_uptime_perfect(db):
    """Valida 100 % de uptime cuando no hay eventos de downtime."""

    org_id = _create_org(db)
    resultado = sla_service.calculate_uptime(org_id, "2026-06", db)

    assert resultado["uptime_percentage"] == 100.0
    assert resultado["downtime_seconds"] == 0
    assert resultado["met_sla"] is True
    assert resultado["organizacion_id"] == org_id
    assert resultado["month"] == "2026-06"


def test_calculate_uptime_with_downtime(db):
    """Valida calculo de uptime con eventos de downtime resueltos."""

    org_id = _create_org(db)
    # 2 horas de downtime = 7200 segundos en junio (30 dias = 2592000 seg)
    evento = SLAEvent(
        organizacion_id=org_id,
        event_type="outage",
        cause="Fallo de red",
        started_at=datetime(2026, 6, 15, tzinfo=timezone.utc),
        ended_at=datetime(2026, 6, 15, 2, 0, tzinfo=timezone.utc),
        duration_seconds=7200,
    )
    db.add(evento)
    db.commit()

    resultado = sla_service.calculate_uptime(org_id, "2026-06", db)

    total_sec = 30 * 86_400  # 2592000
    esperado = round(((total_sec - 7200) / total_sec) * 100, 4)
    assert resultado["uptime_percentage"] == esperado
    assert resultado["downtime_seconds"] == 7200
    # 99.7222 % esta bajo 99.9 % de target SLA
    assert resultado["met_sla"] is False


def test_calculate_uptime_with_multiple_downtime_events(db):
    """Valida suma de multiples eventos de downtime en el mismo mes."""

    org_id = _create_org(db)
    for i in range(3):
        evento = SLAEvent(
            organizacion_id=org_id,
            event_type="outage",
            cause=f"Evento {i + 1}",
            started_at=datetime(2026, 6, 10 + i, tzinfo=timezone.utc),
            ended_at=datetime(2026, 6, 10 + i, 1, 0, tzinfo=timezone.utc),
            duration_seconds=3600,
        )
        db.add(evento)
    db.commit()

    resultado = sla_service.calculate_uptime(org_id, "2026-06", db)

    assert resultado["downtime_seconds"] == 10800  # 3 * 3600


def test_log_downtime_event(db):
    """Valida creacion de un evento de downtime via servicio."""

    org_id = _create_org(db)
    evento = sla_service.log_downtime_event(
        db,
        org_id,
        "outage",
        "Corte de energia",
        started_at=datetime(2026, 6, 10, 8, 0, tzinfo=timezone.utc),
    )

    assert evento.id is not None
    assert evento.organizacion_id == org_id
    assert evento.event_type == "outage"
    assert evento.cause == "Corte de energia"
    assert evento.ended_at is None  # aun no resuelto


def test_log_downtime_event_invalid_type(db):
    """Valida que event_type invalido lance ValueError."""

    with pytest.raises(ValueError, match="event_type debe ser"):
        sla_service.log_downtime_event(db, 1, "invalido", "Razon cualquiera")


def test_resolve_downtime_event(db):
    """Valida cierre de evento y calculo de duracion en segundos."""

    org_id = _create_org(db)
    inicio = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    evento = sla_service.log_downtime_event(
        db,
        org_id,
        "degraded",
        "Degradacion parcial",
        started_at=inicio,
    )

    fin = datetime(2026, 6, 10, 14, 30, tzinfo=timezone.utc)
    resuelto = sla_service.resolve_downtime_event(db, evento.id, ended_at=fin)

    # SQLite no preserva timezone, comparar sin tzinfo
    assert resuelto.ended_at.replace(tzinfo=timezone.utc) == fin
    assert resuelto.duration_seconds == 4 * 3600 + 30 * 60  # 16200


def test_resolve_downtime_event_not_found(db):
    """Valida error 404 al resolver evento inexistente."""

    with pytest.raises(HTTPException) as exc_info:
        sla_service.resolve_downtime_event(db, 9999)
    assert exc_info.value.status_code == 404


def test_resolve_downtime_event_already_resolved(db):
    """Valida que resolver evento ya cerrado no lance error (cambio de estado)."""

    org_id = _create_org(db)
    inicio = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    evento = sla_service.log_downtime_event(
        db, org_id, "maintenance", "Mantencion", started_at=inicio,
    )
    sla_service.resolve_downtime_event(
        db, evento.id,
        ended_at=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
    )

    # Resolver de nuevo con nueva hora
    fin2 = datetime(2026, 6, 10, 15, 0, tzinfo=timezone.utc)
    resuelto = sla_service.resolve_downtime_event(db, evento.id, ended_at=fin2)

    assert resuelto.duration_seconds == 5 * 3600  # 5 horas


def test_generate_monthly_report(db):
    """Valida generacion de reporte mensual con datos de downtime."""

    org_id = _create_org(db)
    evento = SLAEvent(
        organizacion_id=org_id,
        event_type="maintenance",
        cause="Mantenimiento programado",
        started_at=datetime(2026, 6, 20, 22, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 6, 21, 6, 0, tzinfo=timezone.utc),
        duration_seconds=8 * 3600,  # 28800
    )
    db.add(evento)
    db.commit()

    reporte = sla_service.generate_monthly_report(db, org_id, "2026-06")

    assert reporte.id is not None
    assert reporte.month == "2026-06"
    assert reporte.downtime_seconds == 28800
    # 98.8889 % esta bajo 99.9 % de target SLA
    assert reporte.met_sla is False
    assert reporte.credits_amount > 0.0


def test_generate_monthly_report_triggers_credits_on_sla_breach(db):
    """Valida que un incumplimiento SLA genere creditos de penalizacion."""

    org_id = _create_org(db)
    # 1 % de downtime en junio = 25920 segundos; ponemos 26000 para incumplir
    evento = SLAEvent(
        organizacion_id=org_id,
        event_type="outage",
        cause="Fallo masivo",
        started_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        ended_at=datetime(2026, 6, 1, 7, 13, 20, tzinfo=timezone.utc),
        duration_seconds=26000,
    )
    db.add(evento)
    db.commit()

    reporte = sla_service.generate_monthly_report(
        db, org_id, "2026-06",
        sla_target=99.0,
    )

    assert reporte.met_sla is False
    assert reporte.credits_amount > 0


def test_generate_monthly_report_default_sla_target(db):
    """Valida que generate_monthly_report use 99.9 como target por defecto."""

    org_id = _create_org(db)
    reporte = sla_service.generate_monthly_report(db, org_id, "2026-06")

    assert reporte.sla_target == 99.9


def test_sla_compliance_warning(db, monkeypatch):
    """Valida alerta temprana cuando el uptime esta bajo y quedan pocos dias."""

    org_id = _create_org(db)
    # Downtime suficiente para bajar del 99 %
    # Junio: 30 dias = 2592000 segundos
    # 99 % permite 25920 segundos de downtime
    # Ponemos 30000 para incumplir
    evento = SLAEvent(
        organizacion_id=org_id,
        event_type="outage",
        cause="Fallo prolongado",
        started_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        ended_at=datetime(2026, 6, 1, 8, 20, tzinfo=timezone.utc),
        duration_seconds=30000,
    )
    db.add(evento)
    db.commit()

    # Forzar mes actual y dias restantes para el escenario de advertencia
    monkeypatch.setattr(sla_service, "_current_month_str", lambda: "2026-06")
    monkeypatch.setattr(sla_service, "_days_remaining_in_month", lambda: 2)

    resultado = sla_service.check_sla_compliance(db, org_id)

    assert resultado["warning"] is True
    assert resultado["days_remaining"] == 2
    assert resultado["warning_message"] is not None
    assert "uptime actual" in resultado["warning_message"].lower()


def test_sla_compliance_no_warning_when_uptime_healthy(db, monkeypatch):
    """Valida que no se genere warning si el uptime esta sobre el umbral."""

    org_id = _create_org(db)
    monkeypatch.setattr(sla_service, "_current_month_str", lambda: "2026-06")
    monkeypatch.setattr(sla_service, "_days_remaining_in_month", lambda: 2)

    resultado = sla_service.check_sla_compliance(db, org_id)

    assert resultado["warning"] is False
    assert resultado["compliant"] is True
    assert resultado["warning_message"] is None
