"""Endpoints de equipos."""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.models.usuario import Usuario
from app.models.provisioning_token import ProvisioningToken
from app.schemas.equipo import (
    EquipoCreate,
    EquipoFullSetupRequest,
    EquipoFullSetupResponse,
    EquipoResponse,
    EquipoUpdate,
)
from app.services.equipo_service import (
    create_equipo,
    create_equipo_with_umbrales as create_equipo_with_umbrales_service,
    delete_equipo,
    get_equipo_or_404,
    list_equipos,
    update_equipo,
)
from app.schemas.equipo import AutoRegisterRequest, validate_mac_address
from app.config import get_settings
import jwt
from jwt import InvalidTokenError as JWTError
from sqlalchemy.exc import IntegrityError

settings = get_settings()
JWT_ALGORITHM = "HS256"

router = APIRouter(prefix="/equipos", tags=["equipos"])


@router.get(
    "",
    response_model=list[EquipoResponse],
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_equipos(
    request: Request,
    db: Session = Depends(get_db),
) -> list[EquipoResponse]:
    """Lista equipos disponibles."""

    return list_equipos(db)


@router.get(
    "/provisioning-token",
)
def get_provisioning_token(
    request: Request,
    mac_address: str = Query(
        ...,
        min_length=17,
        max_length=17,
        pattern=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
        description="MAC exacta del ESP32 que se va a provisionar",
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> dict:
    """Genera un token seguro para provisionamiento (SoftAP + QR).

    Implementación simple: JWT firmado con SECRET_KEY y propósito 'provision'.
    El token expira en 1 hora.
    Solo accesible por admin/tecnico.
    """

    validated_mac = validate_mac_address(mac_address)
    if validated_mac is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="mac_address es requerida para generar el provisioning token",
        )

    normalized_mac = validated_mac.replace("-", ":").upper()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)
    jti = secrets.token_urlsafe(16)
    payload = {
        "purpose": "provision",
        "expected_mac": normalized_mac,
        "organizacion_id": current_user.organizacion_id,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    db.add(
        ProvisioningToken(
            jti=jti,
            expected_mac=normalized_mac,
            organizacion_id=current_user.organizacion_id,
            expires_at=exp,
        )
    )
    db.commit()

    token = jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)
    return {"token": token, "expires_at": exp.isoformat()}


@router.get(
    "/{equipo_id}",
    response_model=EquipoResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_equipo_by_id(
    equipo_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Obtiene un equipo por identificador."""

    return get_equipo_or_404(db, equipo_id)


@router.post(
    "",
    response_model=EquipoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def post_equipo(
    payload: EquipoCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Crea un equipo persistido."""

    equipo = create_equipo(db, payload)
    response.headers["Location"] = str(
        request.url_for("get_equipo_by_id", equipo_id=str(equipo.id))
    )
    return equipo


@router.put(
    "/{equipo_id}",
    response_model=EquipoResponse,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def put_equipo(
    equipo_id: int,
    payload: EquipoUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Actualiza un equipo persistido."""

    return update_equipo(db, equipo_id, payload)


@router.delete(
    "/{equipo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_equipo_by_id(
    equipo_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """Elimina un equipo por identificador."""

    delete_equipo(db, equipo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/full-setup",
    response_model=EquipoFullSetupResponse,
)
def create_equipo_with_umbrales(
    payload: EquipoFullSetupRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> EquipoFullSetupResponse:
    """Crea equipo con umbrales en una sola transacción atómica.

    La transacción completa vive en el servicio de equipos.
    """
    equipo, umbral_temp, umbral_vib = create_equipo_with_umbrales_service(
        db,
        payload,
        organization_id=current_user.organizacion_id,
    )

    return EquipoFullSetupResponse(
        equipo=equipo,
        umbral_temperatura_id=umbral_temp.id,
        umbral_vibracion_id=umbral_vib.id,
    )


@router.post("/auto-register", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
def auto_register(
    payload: AutoRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Endpoint público para que un dispositivo (ESP32) se registre usando el token.

    Se valida el JWT y se crea un Equipo con la mac_address proporcionada.
    """

    # Validar token
    try:
        claims = jwt.decode(
            payload.token, settings.secret_key, algorithms=[JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )

    if claims.get("purpose") != "provision":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no autorizado para provisioning",
        )

    mac = payload.mac_address
    if not mac:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="mac_address es requerido"
        )

    expected_mac = claims.get("expected_mac")
    if not isinstance(expected_mac, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de provisioning sin MAC asociada",
        )

    normalized_mac = mac.replace("-", ":").upper()
    if normalized_mac != expected_mac.replace("-", ":").upper():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La MAC no coincide con el token de provisioning",
        )

    organization_id = claims.get("organizacion_id")
    if organization_id is not None and not isinstance(organization_id, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de provisioning inválido",
        )

    jti = claims.get("jti")
    if not isinstance(jti, str) or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de provisioning sin identificador",
        )

    # El JWT firmado no basta para impedir replay después de borrar el equipo.
    # Bloquear la fila mantiene el consumo one-shot incluso ante dos requests
    # concurrentes para el mismo dispositivo.
    provisioning_token = db.scalars(
        select(ProvisioningToken).where(ProvisioningToken.jti == jti).with_for_update()
    ).first()
    if (
        provisioning_token is None
        or provisioning_token.expected_mac != normalized_mac
        or provisioning_token.organizacion_id != organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de provisioning no registrado",
        )

    if provisioning_token.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Token de provisioning ya utilizado",
        )

    # Crear equipo mínimo usando nombre por defecto
    from app.schemas.equipo import EquipoCreate

    nombre = f"Equipo {normalized_mac[-5:]}"
    equipo_payload = EquipoCreate(nombre=nombre, mac_address=normalized_mac)

    try:
        equipo = create_equipo(
            db,
            equipo_payload,
            organization_id=organization_id,
            commit=False,
        )
        provisioning_token.used_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(equipo)
    except IntegrityError:
        db.rollback()
        # Probablemente mac_address duplicada
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Equipo con esa MAC ya existe"
        )

    return equipo
