"""Endpoints de facturacion, suscripciones y webhooks de pago."""

import hashlib
import hmac
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.dependencies import get_current_user, get_db, require_role
from app.models.suscripcion import Suscripcion
from app.models.usuario import Usuario
from app.services.billing_service import (
    calcular_revenue_mensual,
    cancelar_suscripcion,
    cambiar_plan,
    crear_suscripcion,
    get_planes_activos,
    procesar_webhook_mercadopago,
    procesar_webhook_stripe,
)

router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schemas internos de request/response
# ---------------------------------------------------------------------------


class PlanResponse(BaseModel):
    id: int
    nombre: str
    slug: str
    precio_mensual: float
    moneda: str
    max_equipos: int
    max_usuarios: int
    sla_target: float
    features: dict | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class SuscripcionResponse(BaseModel):
    id: int
    organizacion_id: int
    plan_id: int
    estado: str
    stripe_subscription_id: str | None = None
    mercadopago_subscription_id: str | None = None
    started_at: datetime | None = None
    ends_at: datetime | None = None
    trial_ends_at: datetime | None = None

    model_config = {"from_attributes": True}


class SuscribirRequest(BaseModel):
    plan_id: int
    payment_method: str = Field(
        ...,
        description='Metodo de pago: "stripe" o "mercadopago"',
    )
    payment_token: str


class CambiarPlanRequest(BaseModel):
    nuevo_plan_id: int


class WebhookResponse(BaseModel):
    acknowledged: bool
    event_type: str
    message: str


class FacturaItem(BaseModel):
    id: int
    fecha: str
    concepto: str
    monto: float
    moneda: str
    estado: str  # pagada | pendiente | fallida


class RevenueResponse(BaseModel):
    mrr: float
    moneda: str
    total_suscripciones: int
    revenue_por_plan: list[dict]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _obtener_org_id_o_error(current_user: Usuario) -> int:
    """Retorna organizacion_id del usuario o lanza 400 si no tiene tenant."""
    org_id = current_user.organizacion_id
    if org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no pertenece a ninguna organizacion. "
            "Contacta al administrador para asignarte un tenant.",
        )
    return org_id


def _obtener_suscripcion_activa_por_org(
    db: Session, org_id: int
) -> Suscripcion:
    """Retorna la suscripcion activa/trial de una organizacion o lanza 404."""
    stmt = (
        select(Suscripcion)
        .where(
            Suscripcion.organizacion_id == org_id,
            Suscripcion.estado.in_(["activa", "trial"]),
        )
        .order_by(Suscripcion.created_at.desc())
        .limit(1)
    )
    suscripcion = db.scalars(stmt).first()
    if suscripcion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una suscripcion activa para esta organizacion.",
        )
    return suscripcion


# ---------------------------------------------------------------------------
# Endpoints publicos
# ---------------------------------------------------------------------------


@router.get("/planes", response_model=list[PlanResponse])
def listar_planes(
    db: Session = Depends(get_db),
) -> list[PlanResponse]:
    """Lista los planes de suscripcion disponibles (publico, sin auth)."""
    planes = get_planes_activos(db)
    return [PlanResponse.model_validate(p) for p in planes]


@router.post("/webhook/stripe", response_model=WebhookResponse)
async def webhook_stripe(
    request: Request,
    db: Session = Depends(get_db),
) -> WebhookResponse:
    """Webhook de Stripe para eventos de facturacion (publico, sin auth).

    Verifica la firma del webhook usando el header Stripe-Signature.
    Si STRIPE_WEBHOOK_SECRET no esta configurado, registra un warning
    y omite la verificacion (solo para desarrollo local).
    """
    body = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if settings.stripe_webhook_secret:
        try:
            import stripe

            stripe.Webhook.construct_event(
                payload=body,
                sig_header=sig_header,
                secret=settings.stripe_webhook_secret,
            )
        except (stripe.error.SignatureVerificationError, ValueError) as e:
            logger.warning("[BILLING] Stripe: firma de webhook invalida: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma de webhook invalida",
            ) from e
    else:
        logger.warning(
            "[BILLING] Stripe: STRIPE_WEBHOOK_SECRET no configurado. "
            "Webhook aceptado sin verificacion de firma (inseguro en produccion)."
        )

    import json

    payload: dict = json.loads(body)
    resultado = procesar_webhook_stripe(db, payload)
    return WebhookResponse(**resultado)


@router.post("/webhook/mercadopago", response_model=WebhookResponse)
async def webhook_mercadopago(
    request: Request,
    db: Session = Depends(get_db),
) -> WebhookResponse:
    """Webhook de MercadoPago para eventos de facturacion (publico, sin auth).

    Verifica la firma HMAC-SHA256 del header x-signature.
    Si MERCADOPAGO_ACCESS_TOKEN no esta configurado, registra un warning
    y omite la verificacion (solo para desarrollo local).
    """
    body = await request.body()
    sig_header = request.headers.get("x-signature", "")

    if settings.mercadopago_access_token and sig_header:
        # MercadoPago firma con HMAC-SHA256 usando el access_token como secret
        expected = hmac.new(
            key=settings.mercadopago_access_token.encode("utf-8"),
            msg=body,
            digestmod=hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, sig_header):
            logger.warning("[BILLING] MercadoPago: firma de webhook invalida")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma de webhook invalida",
            )
    elif not sig_header:
        logger.warning(
            "[BILLING] MercadoPago: header x-signature ausente. "
            "Webhook aceptado sin verificacion."
        )
    else:
        logger.warning(
            "[BILLING] MercadoPago: MERCADOPAGO_ACCESS_TOKEN no configurado. "
            "Webhook aceptado sin verificacion de firma (inseguro en produccion)."
        )

    import json

    payload: dict = json.loads(body)
    resultado = procesar_webhook_mercadopago(db, payload)
    return WebhookResponse(**resultado)


# ---------------------------------------------------------------------------
# Endpoints que requieren autenticacion
# ---------------------------------------------------------------------------


@router.get("/suscripcion", response_model=SuscripcionResponse)
def obtener_suscripcion(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuscripcionResponse:
    """Retorna la suscripcion activa del tenant al que pertenece el usuario.

    Requiere autenticacion.
    El usuario debe pertenecer a una organizacion con suscripcion activa.
    """
    org_id = _obtener_org_id_o_error(current_user)
    suscripcion = _obtener_suscripcion_activa_por_org(db, org_id)
    return SuscripcionResponse.model_validate(suscripcion)


@router.post(
    "/suscribir",
    response_model=SuscripcionResponse,
    status_code=status.HTTP_201_CREATED,
)
def suscribir(
    payload: SuscribirRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuscripcionResponse:
    """Crea una nueva suscripcion para la organizacion del usuario.

    Requiere autenticacion.
    El body debe incluir plan_id, payment_method ('stripe'|'mercadopago')
    y payment_token entregado por el frontend/pasarela.
    """
    org_id = _obtener_org_id_o_error(current_user)

    try:
        suscripcion = crear_suscripcion(
            db=db,
            org_id=org_id,
            plan_id=payload.plan_id,
            payment_method=payload.payment_method,
            payment_token=payload.payment_token,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    return SuscripcionResponse.model_validate(suscripcion)


@router.post("/cancelar", response_model=SuscripcionResponse)
def cancelar(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuscripcionResponse:
    """Cancela la suscripcion activa del tenant del usuario.

    Requiere autenticacion.
    Marca la suscripcion como 'cancelada' y registra ends_at.
    """
    org_id = _obtener_org_id_o_error(current_user)
    suscripcion = _obtener_suscripcion_activa_por_org(db, org_id)

    resultado = cancelar_suscripcion(db, suscripcion.id)
    return SuscripcionResponse.model_validate(resultado)


@router.patch("/cambiar-plan", response_model=SuscripcionResponse)
def cambiar_plan_endpoint(
    payload: CambiarPlanRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuscripcionResponse:
    """Cambia el plan de la suscripcion activa del tenant.

    Requiere autenticacion.
    Calcula prorrateo por el tiempo restante del periodo actual.
    """
    org_id = _obtener_org_id_o_error(current_user)
    suscripcion = _obtener_suscripcion_activa_por_org(db, org_id)

    try:
        resultado = cambiar_plan(
            db=db,
            suscripcion_id=suscripcion.id,
            nuevo_plan_id=payload.nuevo_plan_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    return SuscripcionResponse.model_validate(resultado)


@router.get("/historial", response_model=list[FacturaItem])
def historial_facturas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[FacturaItem]:
    """Retorna el historial de pagos/facturas del tenant.

    Requiere autenticacion.
    NOTA: Actualmente retorna una lista vacia porque el modelo de facturas
    no esta implementado. Se pobla cuando se integre con el proveedor
    de pagos real o se cree la tabla de facturas local.
    """
    # TODO: Implementar cuando exista modelo Factura/Pago en BD.
    # Por ahora se retorna lista vacia como placeholder funcional.
    return []


# ---------------------------------------------------------------------------
# Endpoints administrativos (solo admin)
# ---------------------------------------------------------------------------


@router.get("/admin/revenue", response_model=RevenueResponse)
def revenue_admin(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> RevenueResponse:
    """Retorna metricas de revenue mensual (MRR) para administradores.

    Requiere rol admin.
    Incluye MRR total, cantidad de suscripciones activas y desglose
    por plan.
    """
    revenue = calcular_revenue_mensual(db)
    return RevenueResponse(**revenue)
