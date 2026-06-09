"""Servicios de facturacion, suscripciones y revenue mensual.

Integra con pasarelas de pago externas (Stripe, MercadoPago) de forma
simulada cuando no hay credenciales configuradas.

Configuraciones esperadas en Settings (a agregar en config.py):
    - stripe_secret_key: str = ""
    - stripe_webhook_secret: str = ""
    - mercadopago_access_token: str = ""
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.organizacion import Organizacion
from app.models.suscripcion import Plan, Suscripcion
from app.services.common import get_entity_or_404

logger = logging.getLogger(__name__)

# Prefijos para IDs simulados de suscripcion externa
_SIMULATED_STRIPE_PREFIX = "sub_stripe_sim_"
_SIMULATED_MP_PREFIX = "sub_mp_sim_"


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


def _simular_pago_stripe(payment_token: str) -> str:
    """Simula la creacion de una suscripcion en Stripe y retorna un ID ficticio.

    Si las credenciales de Stripe estan configuradas en Settings, se intentaria
    la integracion real. Por ahora siempre simula.
    """
    settings = get_settings()
    stripe_key = getattr(settings, "stripe_secret_key", "")
    if stripe_key:
        logger.info(
            "[BILLING] Stripe key presente (longitud=%d), integracion real no implementada. "
            "Simulando creacion.",
            len(stripe_key),
        )

    sufixo = payment_token[-8:] if len(payment_token) >= 8 else payment_token
    sub_id = f"{_SIMULATED_STRIPE_PREFIX}{sufixo}"
    logger.info(
        "[BILLING] Suscripcion Stripe simulada creada: sub_id=%s", sub_id
    )
    return sub_id


def _simular_pago_mercadopago(payment_token: str) -> str:
    """Simula la creacion de una suscripcion en MercadoPago y retorna un ID ficticio.

    Si las credenciales de MercadoPago estan configuradas en Settings, se intentaria
    la integracion real. Por ahora siempre simula.
    """
    settings = get_settings()
    mp_token = getattr(settings, "mercadopago_access_token", "")
    if mp_token:
        logger.info(
            "[BILLING] MercadoPago token presente (longitud=%d), integracion real no implementada. "
            "Simulando creacion.",
            len(mp_token),
        )

    sufixo = payment_token[-8:] if len(payment_token) >= 8 else payment_token
    sub_id = f"{_SIMULATED_MP_PREFIX}{sufixo}"
    logger.info(
        "[BILLING] Suscripcion MercadoPago simulada creada: sub_id=%s", sub_id
    )
    return sub_id


def _calcular_prorrateo(
    plan_actual: Plan, plan_nuevo: Plan, suscripcion: Suscripcion
) -> dict:
    """Calcula el credito o cargo por cambio de plan con prorrateo simple.

    Toma el tiempo restante del periodo actual (asumiendo ciclo mensual desde
    started_at) y calcula:
      - credito por la parte no usada del plan actual
      - cargo por la parte del nuevo plan que se usara
      - diferencia neta (positivo = credito, negativo = cargo adicional)

    Retorna un dict con credit_amount, charge_amount, net_amount y
    remaining_days.
    """
    now = datetime.now(timezone.utc)
    start = suscripcion.started_at
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    # Ciclo mensual: 30 dias como aproximacion
    ciclo_segundos = 30 * 86_400
    transcurrido = int((now - start).total_seconds())
    fraccion_usada = min(max(transcurrido / ciclo_segundos, 0.0), 1.0)
    fraccion_restante = 1.0 - fraccion_usada
    remaining_days = round(fraccion_restante * 30, 1)

    credito_plan_actual = round(plan_actual.precio_mensual * fraccion_restante, 2)
    cargo_plan_nuevo = round(plan_nuevo.precio_mensual * fraccion_restante, 2)
    neto = round(credito_plan_actual - cargo_plan_nuevo, 2)

    return {
        "remaining_days": remaining_days,
        "credit_amount": credito_plan_actual,
        "charge_amount": cargo_plan_nuevo,
        "net_amount": neto,
    }


def _obtener_plan_por_id(db: Session, plan_id: int) -> Plan:
    """Obtiene un Plan por ID o lanza 404."""
    return get_entity_or_404(db, Plan, plan_id, "Plan no encontrado")


def _obtener_suscripcion(db: Session, suscripcion_id: int) -> Suscripcion:
    """Obtiene una Suscripcion por ID o lanza 404."""
    return get_entity_or_404(
        db, Suscripcion, suscripcion_id, "Suscripcion no encontrada"
    )


# ---------------------------------------------------------------------------
# Funciones publicas
# ---------------------------------------------------------------------------


def get_planes_activos(db: Session) -> list[Plan]:
    """Retorna la lista de planes de suscripcion disponibles (activos).

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.

    Retorna
    -------
    list[Plan]
        Lista de planes marcados como activos.
    """
    stmt = select(Plan).where(Plan.is_active.is_(True)).order_by(Plan.precio_mensual)
    result = list(db.scalars(stmt))
    logger.debug("[BILLING] Planes activos consultados: %d", len(result))
    return result


def crear_suscripcion(
    db: Session,
    org_id: int,
    plan_id: int,
    payment_method: str,
    payment_token: str,
) -> Suscripcion:
    """Crea una nueva suscripcion para una organizacion.

    Segun el metodo de pago, integra con la pasarela correspondiente
    (simulada si no hay credenciales configuradas):
      - "stripe"      -> Stripe API
      - "mercadopago" -> MercadoPago API
      - cualquier otro -> ValueError

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    org_id : int
        Identificador de la organizacion.
    plan_id : int
        Identificador del plan a suscribir.
    payment_method : str
        Metodo de pago: "stripe" o "mercadopago".
    payment_token : str
        Token de pago entregado por el frontend/pasarela.

    Retorna
    -------
    Suscripcion
        La suscripcion recien creada.

    Lanza
    -----
    ValueError
        Si el metodo de pago no es soportado.
    """
    # Validar que la organizacion existe
    get_entity_or_404(db, Organizacion, org_id, "Organizacion no encontrada")

    # Validar que el plan existe y esta activo
    plan = _obtener_plan_por_id(db, plan_id)
    if not plan.is_active:
        raise ValueError(f"El plan '{plan.nombre}' no esta disponible actualmente")

    # Procesar pago segun el metodo
    payment_method = payment_method.strip().lower()
    stripe_sub_id = None
    mercadopago_sub_id = None

    if payment_method == "stripe":
        stripe_sub_id = _simular_pago_stripe(payment_token)
    elif payment_method == "mercadopago":
        mercadopago_sub_id = _simular_pago_mercadopago(payment_token)
    else:
        raise ValueError(
            f"Metodo de pago no soportado: '{payment_method}'. "
            "Use 'stripe' o 'mercadopago'."
        )

    # Crear suscripcion en BD
    now = datetime.now(timezone.utc)
    suscripcion = Suscripcion(
        organizacion_id=org_id,
        plan_id=plan_id,
        estado="activa",
        stripe_subscription_id=stripe_sub_id,
        mercadopago_subscription_id=mercadopago_sub_id,
        started_at=now,
    )
    db.add(suscripcion)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "[BILLING] Error al crear suscripcion: org_id=%d plan_id=%d method=%s",
            org_id,
            plan_id,
            payment_method,
        )
        raise

    db.refresh(suscripcion)
    logger.info(
        "[BILLING] Suscripcion creada: id=%d org_id=%d plan=%s metodo=%s",
        suscripcion.id,
        org_id,
        plan.nombre,
        payment_method,
    )
    return suscripcion


def cancelar_suscripcion(db: Session, suscripcion_id: int) -> Suscripcion:
    """Cancela una suscripcion activa.

    Marca la suscripcion como "cancelada" y registra ends_at con la fecha
    y hora actual UTC.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    suscripcion_id : int
        Identificador de la suscripcion a cancelar.

    Retorna
    -------
    Suscripcion
        La suscripcion actualizada.
    """
    suscripcion = _obtener_suscripcion(db, suscripcion_id)

    if suscripcion.estado == "cancelada":
        logger.warning(
            "[BILLING] Intento de cancelar suscripcion ya cancelada: id=%d",
            suscripcion_id,
        )
        return suscripcion

    suscripcion.estado = "cancelada"
    suscripcion.ends_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "[BILLING] Error al cancelar suscripcion: id=%d", suscripcion_id
        )
        raise

    db.refresh(suscripcion)
    logger.info(
        "[BILLING] Suscripcion cancelada: id=%d org_id=%d plan_id=%d",
        suscripcion.id,
        suscripcion.organizacion_id,
        suscripcion.plan_id,
    )
    return suscripcion


def cambiar_plan(
    db: Session,
    suscripcion_id: int,
    nuevo_plan_id: int,
) -> Suscripcion:
    """Cambia el plan de una suscripcion activa con prorrateo simple.

    Calcula el credito/cargo proporcional al tiempo restante del periodo
    actual y actualiza la referencia al nuevo plan.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    suscripcion_id : int
        Identificador de la suscripcion.
    nuevo_plan_id : int
        Identificador del nuevo plan.

    Retorna
    -------
    Suscripcion
        La suscripcion actualizada con el nuevo plan.
    """
    suscripcion = _obtener_suscripcion(db, suscripcion_id)

    if suscripcion.estado != "activa":
        raise ValueError(
            f"No se puede cambiar el plan de una suscripcion en estado "
            f"'{suscripcion.estado}'. Solo suscripciones activas."
        )

    plan_actual = _obtener_plan_por_id(db, suscripcion.plan_id)
    plan_nuevo = _obtener_plan_por_id(db, nuevo_plan_id)

    if not plan_nuevo.is_active:
        raise ValueError(f"El plan '{plan_nuevo.nombre}' no esta disponible actualmente")

    if plan_actual.id == plan_nuevo.id:
        logger.info(
            "[BILLING] Cambio de plan al mismo plan: suscripcion_id=%d plan_id=%d",
            suscripcion_id,
            plan_actual.id,
        )
        return suscripcion

    # Calcular prorrateo
    prorrateo = _calcular_prorrateo(plan_actual, plan_nuevo, suscripcion)

    # Actualizar al nuevo plan
    suscripcion.plan_id = nuevo_plan_id

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "[BILLING] Error al cambiar plan: suscripcion_id=%d nuevo_plan=%d",
            suscripcion_id,
            nuevo_plan_id,
        )
        raise

    db.refresh(suscripcion)
    logger.info(
        "[BILLING] Plan cambiado: suscripcion_id=%d plan_actual=%s plan_nuevo=%s "
        "prorrateo=%s",
        suscripcion.id,
        plan_actual.nombre,
        plan_nuevo.nombre,
        prorrateo,
    )
    return suscripcion


def procesar_webhook_stripe(db: Session, payload: dict) -> dict:
    """Procesa un evento entrante desde el webhook de Stripe.

    Reconoce los tipos de evento:
      - invoice.paid         -> confirma pago
      - invoice.payment_failed -> registra fallo
      - customer.subscription.deleted -> cancela suscripcion local

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    payload : dict
        Cuerpo del evento enviado por Stripe (debe incluir 'type' y 'data').

    Retorna
    -------
    dict
        Contiene 'acknowledged' (bool), 'event_type' (str) y un mensaje
        informativo.
    """
    event_type = payload.get("type", "unknown")
    event_data = payload.get("data", {}).get("object", {})
    logger.info("[BILLING] Webhook Stripe recibido: type=%s", event_type)

    resultado = {
        "acknowledged": True,
        "event_type": event_type,
        "message": "Evento procesado",
    }

    if event_type == "invoice.paid":
        subscription_id = event_data.get("subscription", "")
        logger.info(
            "[BILLING] Stripe: factura pagada subscription=%s", subscription_id
        )
        resultado["message"] = "Factura pagada registrada"

    elif event_type == "invoice.payment_failed":
        subscription_id = event_data.get("subscription", "")
        logger.warning(
            "[BILLING] Stripe: pago fallido subscription=%s", subscription_id
        )
        resultado["message"] = "Fallo de pago registrado"

    elif event_type == "customer.subscription.deleted":
        subscription_id = event_data.get("id", "")
        # Intentar cancelar suscripcion local si existe el ID externo
        stmt = select(Suscripcion).where(
            Suscripcion.stripe_subscription_id == subscription_id,
            Suscripcion.estado != "cancelada",
        )
        suscripcion = db.scalars(stmt).first()
        if suscripcion is not None:
            suscripcion.estado = "cancelada"
            suscripcion.ends_at = datetime.now(timezone.utc)
            try:
                db.commit()
                logger.info(
                    "[BILLING] Stripe: suscripcion cancelada por webhook: local_id=%d",
                    suscripcion.id,
                )
            except SQLAlchemyError:
                db.rollback()
                logger.exception(
                    "[BILLING] Stripe: error al cancelar suscripcion local "
                    "por webhook: sub_id=%s",
                    subscription_id,
                )
        else:
            logger.info(
                "[BILLING] Stripe: suscripcion externa %s no encontrada localmente "
                "(puede haberse cancelado antes)",
                subscription_id,
            )
        resultado["message"] = "Suscripcion cancelada por webhook"

    else:
        logger.debug("[BILLING] Stripe: evento no manejado type=%s", event_type)
        resultado["message"] = f"Evento '{event_type}' recibido pero no manejado"

    return resultado


def procesar_webhook_mercadopago(db: Session, payload: dict) -> dict:
    """Procesa un evento entrante desde el webhook de MercadoPago.

    Reconoce los tipos de evento:
      - subscription_updated   -> actualiza estado local
      - subscription_cancelled -> cancela suscripcion local

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    payload : dict
        Cuerpo del evento enviado por MercadoPago.

    Retorna
    -------
    dict
        Contiene 'acknowledged' (bool), 'event_type' (str) y un mensaje.
    """
    event_type = payload.get("type", "unknown")
    event_data = payload.get("data", {})
    logger.info("[BILLING] Webhook MercadoPago recibido: type=%s", event_type)

    resultado = {
        "acknowledged": True,
        "event_type": event_type,
        "message": "Evento procesado",
    }

    if event_type == "subscription_updated":
        mp_sub_id = event_data.get("id", "")
        status = event_data.get("status", "")
        logger.info(
            "[BILLING] MercadoPago: suscripcion actualizada id=%s status=%s",
            mp_sub_id,
            status,
        )
        resultado["message"] = f"Suscripcion actualizada a estado '{status}'"

    elif event_type == "subscription_cancelled":
        mp_sub_id = event_data.get("id", "")
        stmt = select(Suscripcion).where(
            Suscripcion.mercadopago_subscription_id == mp_sub_id,
            Suscripcion.estado != "cancelada",
        )
        suscripcion = db.scalars(stmt).first()
        if suscripcion is not None:
            suscripcion.estado = "cancelada"
            suscripcion.ends_at = datetime.now(timezone.utc)
            try:
                db.commit()
                logger.info(
                    "[BILLING] MercadoPago: suscripcion cancelada por webhook: "
                    "local_id=%d",
                    suscripcion.id,
                )
            except SQLAlchemyError:
                db.rollback()
                logger.exception(
                    "[BILLING] MercadoPago: error al cancelar suscripcion local "
                    "por webhook: sub_id=%s",
                    mp_sub_id,
                )
        else:
            logger.info(
                "[BILLING] MercadoPago: suscripcion externa %s no encontrada "
                "localmente",
                mp_sub_id,
            )
        resultado["message"] = "Suscripcion cancelada por webhook"

    else:
        logger.debug(
            "[BILLING] MercadoPago: evento no manejado type=%s", event_type
        )
        resultado["message"] = f"Evento '{event_type}' recibido pero no manejado"

    return resultado


def calcular_revenue_mensual(db: Session) -> dict:
    """Calcula metricas de revenue mensual (MRR) y desglose por plan.

    Considera solamente suscripciones activas al momento de la consulta.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.

    Retorna
    -------
    dict
        Contiene:
          - mrr (float): Monthly Recurring Revenue total
          - total_suscripciones (int): cantidad de suscripciones activas
          - revenue_por_plan (list[dict]): cada entrada tiene plan_id, nombre,
            precio_mensual, cantidad, subtotal
          - moneda (str): moneda base (se toma del primer plan, "CLP" por defecto)
    """
    # Obtener todas las suscripciones activas con su plan
    stmt = (
        select(Suscripcion, Plan)
        .join(Plan, Suscripcion.plan_id == Plan.id)
        .where(Suscripcion.estado == "activa")
    )
    rows = db.execute(stmt).all()

    # Agrupar por plan
    agrupado: dict[int, dict] = {}
    for suscripcion, plan in rows:
        if plan.id not in agrupado:
            agrupado[plan.id] = {
                "plan_id": plan.id,
                "nombre": plan.nombre,
                "precio_mensual": plan.precio_mensual,
                "moneda": plan.moneda,
                "cantidad": 0,
                "subtotal": 0.0,
            }
        agrupado[plan.id]["cantidad"] += 1
        agrupado[plan.id]["subtotal"] = round(
            agrupado[plan.id]["cantidad"] * plan.precio_mensual, 2
        )

    revenue_por_plan = list(agrupado.values())
    mrr = round(sum(item["subtotal"] for item in revenue_por_plan), 2)
    total_suscripciones = sum(item["cantidad"] for item in revenue_por_plan)

    moneda = revenue_por_plan[0]["moneda"] if revenue_por_plan else "CLP"

    logger.info(
        "[BILLING] Revenue mensual calculado: MRR=%.2f %s suscripciones=%d planes=%d",
        mrr,
        moneda,
        total_suscripciones,
        len(revenue_por_plan),
    )

    return {
        "mrr": mrr,
        "moneda": moneda,
        "total_suscripciones": total_suscripciones,
        "revenue_por_plan": revenue_por_plan,
    }
