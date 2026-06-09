"""Tests del servicio de notificaciones (Twilio WhatsApp/SMS)."""

from types import SimpleNamespace

from app.services import notification_service as ns


def test_send_whatsapp_missing_credentials(monkeypatch):
    """Valida error elegante cuando no hay credenciales Twilio para WhatsApp."""

    monkeypatch.setattr(ns, "_tiene_credenciales", lambda: False)

    service = ns.NotificationService()
    resultado = service.send_whatsapp("+56912345678", "Mensaje de prueba")

    assert resultado["sent"] is False
    assert resultado["channel"] == "whatsapp"
    assert resultado["error"] is not None
    assert "Configuracion" in resultado["error"] or "incompleta" in resultado["error"]


def test_send_sms_missing_credentials(monkeypatch):
    """Valida error elegante cuando no hay credenciales Twilio para SMS."""

    monkeypatch.setattr(ns, "_tiene_credenciales", lambda: False)

    service = ns.NotificationService()
    resultado = service.send_sms("+56987654321", "Mensaje SMS de prueba")

    assert resultado["sent"] is False
    assert resultado["channel"] == "sms"
    assert resultado["error"] is not None


def test_send_whatsapp_missing_credentials_uses_correct_channel(monkeypatch):
    """Valida que el canal en la respuesta sea 'whatsapp', no 'sms'."""

    monkeypatch.setattr(ns, "_tiene_credenciales", lambda: False)

    service = ns.NotificationService()
    resultado = service.send_whatsapp("+56911111111", "Test")

    assert resultado["channel"] == "whatsapp"
    assert resultado["sent"] is False


def test_send_critical_alert_logs_to_audit(db, monkeypatch):
    """Valida que send_critical_alert registre en audit log al enviar."""

    import app.services.audit_service as audit_svc

    audit_calls: list[dict] = []

    def _fake_log_audit(**kwargs):
        audit_calls.append(kwargs)
        from app.models.audit_log import AuditLog

        log = AuditLog(
            usuario_id=kwargs.get("usuario_id"),
            action=kwargs["action"],
            entity_type=kwargs["entity_type"],
            entity_id=kwargs.get("entity_id"),
            new_values=kwargs.get("new_values"),
        )
        db.add(log)
        db.commit()
        return log

    monkeypatch.setattr(ns, "_tiene_credenciales", lambda: True)
    monkeypatch.setattr(audit_svc, "log_audit", _fake_log_audit)

    def _fake_wa(_to, _msg):
        return SimpleNamespace(
            sent=True,
            sid="SMwhatsapp_test_123",
            error=None,
            model_dump=lambda: {
                "sent": True,
                "channel": "whatsapp",
                "sid": "SMwhatsapp_test_123",
                "message": "Alerta critica",
                "to_number": "+569****5678",
                "error": None,
            },
        )

    monkeypatch.setattr(ns, "_ejecutar_envio_whatsapp", _fake_wa)

    user = SimpleNamespace(id=42, telefono="+56912345678")
    service = ns.NotificationService()
    resultado = service.send_critical_alert(user, "Alerta critica de prueba", db)

    assert resultado["sent"] is True
    assert resultado["sid"] == "SMwhatsapp_test_123"

    # Verificar que se llamo a log_audit al menos una vez
    assert len(audit_calls) >= 1
    last_audit = audit_calls[-1]
    assert last_audit["action"] == "send_critical_alert"
    assert last_audit["entity_type"] == "notificacion"
    assert last_audit["usuario_id"] == 42


def test_send_critical_alert_logs_audit_on_failure(db, monkeypatch):
    """Valida que send_critical_alert registre audit incluso cuando falla."""

    import app.services.audit_service as audit_svc

    audit_calls: list[dict] = []

    def _fake_log_audit(**kwargs):
        audit_calls.append(kwargs)
        from app.models.audit_log import AuditLog

        log = AuditLog(
            usuario_id=kwargs.get("usuario_id"),
            action=kwargs["action"],
            entity_type=kwargs["entity_type"],
            entity_id=kwargs.get("entity_id"),
            new_values=kwargs.get("new_values"),
        )
        db.add(log)
        db.commit()
        return log

    monkeypatch.setattr(ns, "_tiene_credenciales", lambda: True)
    monkeypatch.setattr(audit_svc, "log_audit", _fake_log_audit)

    def _fake_wa_fail(_to, _msg):
        return SimpleNamespace(
            sent=False,
            sid=None,
            error="Error Twilio API: 63003",
            model_dump=lambda: {
                "sent": False,
                "channel": "whatsapp",
                "error": "Error Twilio API: 63003",
                "message": "Alerta critica",
                "to_number": "+569****5678",
                "sid": None,
            },
        )

    def _fake_sms_fail(_to, _msg):
        return SimpleNamespace(
            sent=False,
            sid=None,
            error="Limite alcanzado",
            model_dump=lambda: {
                "sent": False,
                "channel": "sms",
                "error": "Limite alcanzado",
                "message": "Alerta critica",
                "to_number": "+569****5678",
                "sid": None,
            },
        )

    monkeypatch.setattr(ns, "_ejecutar_envio_whatsapp", _fake_wa_fail)
    monkeypatch.setattr(ns, "_ejecutar_envio_sms", _fake_sms_fail)

    user = SimpleNamespace(id=7, telefono="+56987654321")
    service = ns.NotificationService()
    resultado = service.send_critical_alert(user, "Alerta critica", db)

    assert resultado["sent"] is False
    # Debe haber audit log para el intento con ambos canales fallidos
    assert len(audit_calls) >= 1
    last_audit = audit_calls[-1]
    assert last_audit["action"] == "send_critical_alert"


def test_send_critical_alert_no_phone_logs_audit(db, monkeypatch):
    """Valida audit cuando el usuario no tiene telefono registrado."""

    import app.services.audit_service as audit_svc

    audit_calls: list[dict] = []

    def _fake_log_audit(**kwargs):
        audit_calls.append(kwargs)
        return SimpleNamespace(id=1)

    monkeypatch.setattr(ns, "_tiene_credenciales", lambda: True)
    monkeypatch.setattr(audit_svc, "log_audit", _fake_log_audit)

    user = SimpleNamespace(id=99, telefono=None)
    service = ns.NotificationService()
    resultado = service.send_critical_alert(user, "Test sin telefono", db)

    assert resultado["sent"] is False
    assert "telefono" in resultado["error"].lower()
    assert len(audit_calls) >= 1
