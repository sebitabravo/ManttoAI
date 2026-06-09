"""Tests del servicio de facturacion, suscripciones y revenue mensual."""

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.models.organizacion import Organizacion
from app.models.suscripcion import Plan, Suscripcion
from app.services import billing_service


def _create_org(db, nombre: str = "Org Billing", slug: str = "org-billing") -> int:
    """Crea una organizacion auxiliar y retorna su id."""

    org = Organizacion(nombre=nombre, slug=slug)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org.id


def _create_plan(
    db,
    nombre: str = "Premium",
    slug: str = "premium",
    precio: float = 50000.0,
    max_equipos: int = 20,
    max_usuarios: int = 10,
    is_active: bool = True,
) -> int:
    """Crea un plan auxiliar y retorna su id."""

    plan = Plan(
        nombre=nombre,
        slug=slug,
        precio_mensual=precio,
        max_equipos=max_equipos,
        max_usuarios=max_usuarios,
        is_active=is_active,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan.id


def test_get_planes_activos(db):
    """Valida que get_planes_activos retorne solo planes activos ordenados por precio."""

    _create_plan(db, "Basico", "basico", precio=10000, max_equipos=5, max_usuarios=2)
    _create_plan(db, "Premium", "premium", precio=50000, max_equipos=20, max_usuarios=10)
    _create_plan(
        db, "Inactivo", "inactivo", precio=20000, max_equipos=10, max_usuarios=5,
        is_active=False,
    )

    planes = billing_service.get_planes_activos(db)

    assert len(planes) == 2
    assert all(p.is_active for p in planes)
    nombres = [p.nombre for p in planes]
    assert "Basico" in nombres
    assert "Premium" in nombres
    assert "Inactivo" not in nombres


def test_crear_suscripcion(db):
    """Valida creacion de suscripcion con metodo Stripe."""

    org_id = _create_org(db)
    plan_id = _create_plan(db)

    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_id, "stripe", "tok_test_abcdef12",
    )

    assert suscripcion.id is not None
    assert suscripcion.organizacion_id == org_id
    assert suscripcion.plan_id == plan_id
    assert suscripcion.estado == "activa"
    assert suscripcion.stripe_subscription_id is not None
    assert "sub_stripe_sim_" in suscripcion.stripe_subscription_id
    assert suscripcion.started_at is not None


def test_crear_suscripcion_mercadopago(db):
    """Valida creacion de suscripcion con metodo MercadoPago."""

    org_id = _create_org(db, slug="org-mp")
    plan_id = _create_plan(db, slug="plan-mp")

    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_id, "mercadopago", "tok_mp_98765432",
    )

    assert suscripcion.id is not None
    assert suscripcion.estado == "activa"
    assert suscripcion.mercadopago_subscription_id is not None
    assert "sub_mp_sim_" in suscripcion.mercadopago_subscription_id


def test_crear_suscripcion_invalid_org(db):
    """Valida error 404 al crear suscripcion con organizacion inexistente."""

    plan_id = _create_plan(db)

    with pytest.raises(HTTPException) as exc_info:
        billing_service.crear_suscripcion(db, 9999, plan_id, "stripe", "tok_test")
    assert exc_info.value.status_code == 404


def test_crear_suscripcion_inactive_plan(db):
    """Valida error al crear suscripcion con plan inactivo."""

    org_id = _create_org(db, slug="org-inactive")
    plan_id = _create_plan(
        db, "Inactivo", "inactivo-plan", precio=30000, is_active=False,
    )

    with pytest.raises(ValueError, match="no esta disponible"):
        billing_service.crear_suscripcion(db, org_id, plan_id, "stripe", "tok_test")


def test_crear_suscripcion_unsupported_method(db):
    """Valida error al usar metodo de pago no soportado."""

    org_id = _create_org(db, slug="org-unsupported")
    plan_id = _create_plan(db, slug="plan-unsupported")

    with pytest.raises(ValueError, match="Metodo de pago no soportado"):
        billing_service.crear_suscripcion(
            db, org_id, plan_id, "paypal", "tok_paypal",
        )


def test_cancelar_suscripcion(db):
    """Valida cancelacion de suscripcion activa."""

    org_id = _create_org(db, slug="org-cancel")
    plan_id = _create_plan(db, slug="plan-cancel")
    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_id, "stripe", "tok_cancel_1234",
    )

    cancelada = billing_service.cancelar_suscripcion(db, suscripcion.id)

    assert cancelada.estado == "cancelada"
    assert cancelada.ends_at is not None
    assert cancelada.id == suscripcion.id


def test_cancelar_suscripcion_not_found(db):
    """Valida error 404 al cancelar suscripcion inexistente."""

    with pytest.raises(HTTPException) as exc_info:
        billing_service.cancelar_suscripcion(db, 9999)
    assert exc_info.value.status_code == 404


def test_cancelar_suscripcion_already_cancelled(db):
    """Valida que cancelar una suscripcion ya cancelada no lance error."""

    org_id = _create_org(db, slug="org-double-cancel")
    plan_id = _create_plan(db, slug="plan-double-cancel")
    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_id, "stripe", "tok_double_cancel",
    )
    billing_service.cancelar_suscripcion(db, suscripcion.id)

    # Segundo intento no debe fallar
    cancelada = billing_service.cancelar_suscripcion(db, suscripcion.id)
    assert cancelada.estado == "cancelada"


def test_cambiar_plan(db):
    """Valida cambio de plan con prorrateo."""

    org_id = _create_org(db, slug="org-change")
    plan_basico_id = _create_plan(
        db, "Basico", "basico-change", precio=10000, max_equipos=5, max_usuarios=2,
    )
    plan_premium_id = _create_plan(
        db, "Premium", "premium-change", precio=50000, max_equipos=20, max_usuarios=10,
    )

    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_basico_id, "stripe", "tok_change_plan",
    )

    cambiada = billing_service.cambiar_plan(db, suscripcion.id, plan_premium_id)

    assert cambiada.plan_id == plan_premium_id
    assert cambiada.id == suscripcion.id


def test_cambiar_plan_same_plan(db):
    """Valida que cambiar al mismo plan no modifique nada."""

    org_id = _create_org(db, slug="org-same-plan")
    plan_id = _create_plan(db, slug="same-plan")
    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_id, "stripe", "tok_same_plan",
    )

    cambiada = billing_service.cambiar_plan(db, suscripcion.id, plan_id)

    assert cambiada.plan_id == plan_id


def test_cambiar_plan_not_active(db):
    """Valida error al cambiar a un plan inactivo."""

    org_id = _create_org(db, slug="org-change-inactive")
    plan_activo_id = _create_plan(db, "Activo", "activo-change", precio=10000, max_equipos=5, max_usuarios=2)
    plan_inactivo_id = _create_plan(
        db, "Inactivo", "inactivo-change", precio=20000, max_equipos=10, max_usuarios=5,
        is_active=False,
    )
    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_activo_id, "stripe", "tok_change_inactive",
    )

    with pytest.raises(ValueError, match="no esta disponible"):
        billing_service.cambiar_plan(db, suscripcion.id, plan_inactivo_id)


def test_cambiar_plan_cancelled_subscription(db):
    """Valida error al cambiar plan de una suscripcion cancelada."""

    org_id = _create_org(db, slug="org-change-cancelled")
    plan_a_id = _create_plan(db, "Plan A", "plan-a", precio=10000, max_equipos=5, max_usuarios=2)
    plan_b_id = _create_plan(db, "Plan B", "plan-b", precio=20000, max_equipos=10, max_usuarios=5)
    suscripcion = billing_service.crear_suscripcion(
        db, org_id, plan_a_id, "stripe", "tok_cancelled_change",
    )
    billing_service.cancelar_suscripcion(db, suscripcion.id)

    with pytest.raises(ValueError, match="estado"):
        billing_service.cambiar_plan(db, suscripcion.id, plan_b_id)


def test_calcular_revenue(db):
    """Valida calculo de revenue mensual (MRR) con multiples suscripciones."""

    org1_id = _create_org(db, "Org 1", "org-rev-1")
    org2_id = _create_org(db, "Org 2", "org-rev-2")
    plan_id = _create_plan(db, "Premium", "premium-rev", precio=50000, max_equipos=20, max_usuarios=10)

    for org_id in [org1_id, org2_id]:
        sub = Suscripcion(
            organizacion_id=org_id,
            plan_id=plan_id,
            estado="activa",
            started_at=datetime.now(timezone.utc),
        )
        db.add(sub)
    db.commit()

    revenue = billing_service.calcular_revenue_mensual(db)

    assert revenue["mrr"] == 100000.0  # 2 * 50000
    assert revenue["total_suscripciones"] == 2
    assert len(revenue["revenue_por_plan"]) == 1
    assert revenue["revenue_por_plan"][0]["subtotal"] == 100000.0
    assert revenue["revenue_por_plan"][0]["cantidad"] == 2


def test_calcular_revenue_excludes_cancelled(db):
    """Valida que suscripciones canceladas no se incluyan en MRR."""

    org1_id = _create_org(db, "Org Rev 1", "org-rev-x1")
    org2_id = _create_org(db, "Org Rev 2", "org-rev-x2")
    plan_id = _create_plan(db, "Basico", "basico-rev-x", precio=10000, max_equipos=5, max_usuarios=2)

    sub1 = Suscripcion(
        organizacion_id=org1_id, plan_id=plan_id, estado="activa",
        started_at=datetime.now(timezone.utc),
    )
    sub2 = Suscripcion(
        organizacion_id=org2_id, plan_id=plan_id, estado="cancelada",
        started_at=datetime.now(timezone.utc), ends_at=datetime.now(timezone.utc),
    )
    db.add_all([sub1, sub2])
    db.commit()

    revenue = billing_service.calcular_revenue_mensual(db)

    assert revenue["total_suscripciones"] == 1
    assert revenue["mrr"] == 10000.0


def test_calcular_revenue_empty(db):
    """Valida revenue vacio cuando no hay suscripciones."""

    revenue = billing_service.calcular_revenue_mensual(db)

    assert revenue["mrr"] == 0.0
    assert revenue["total_suscripciones"] == 0
    assert revenue["revenue_por_plan"] == []
    assert revenue["moneda"] == "CLP"
