"""Endpoints de equipos."""

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.usuario import Usuario
from app.schemas.equipo import (
    EquipoCreate,
    EquipoFullSetupRequest,
    EquipoFullSetupResponse,
    EquipoResponse,
    EquipoUpdate,
)
from app.services.equipo_service import (
    create_equipo,
    delete_equipo,
    get_equipo_or_404,
    list_equipos,
    update_equipo,
)
from app.schemas.equipo import AutoRegisterRequest
from app.config import get_settings
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
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
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def get_provisioning_token(request: Request) -> dict:
    """Genera un token seguro para provisionamiento (SoftAP + QR).

    Implementación simple: JWT firmado con SECRET_KEY y propósito 'provision'.
    El token expira en 1 hora.
    Solo accesible por admin/tecnico.
    """

    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)
    payload = {
        "purpose": "provision",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

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
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def create_equipo_with_umbrales(
    payload: EquipoFullSetupRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> EquipoFullSetupResponse:
    """Crea equipo con umbrales en una sola transacción atómica.

    Se realiza commit al final si todo sale bien y rollback ante cualquier error.
    """
    from app.models.equipo import Equipo
    from app.models.umbral import Umbral

    try:
        # 1. Crear equipo
        equipo = Equipo(
            nombre=payload.nombre,
            ubicacion=payload.ubicacion or "Laboratorio",
            tipo=payload.tipo or "Motor",
            rubro=payload.rubro,
            descripcion=payload.descripcion or "Equipo monitoreado por ManttoAI",
            estado="operativo",
        )
        db.add(equipo)
        db.flush()  # Obtener ID

        # 2. Crear umbral de temperatura
        umbral_temp = Umbral(
            equipo_id=equipo.id,
            variable="temperatura",
            valor_min=0,
            valor_max=payload.temperatura_max,
        )
        db.add(umbral_temp)
        db.flush()

        # 3. Crear umbral de vibración
        umbral_vib = Umbral(
            equipo_id=equipo.id,
            variable="vibracion",
            valor_min=0,
            valor_max=payload.vibracion_max,
        )
        db.add(umbral_vib)
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        raise

    return EquipoFullSetupResponse(
        equipo=equipo,
        umbral_temperatura_id=umbral_temp.id,
        umbral_vibracion_id=umbral_vib.id,
    )


@router.post("/auto-register", status_code=status.HTTP_201_CREATED)
def auto_register(payload: AutoRegisterRequest, db: Session = Depends(get_db)):
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

    # Crear equipo mínimo usando nombre por defecto
    from app.schemas.equipo import EquipoCreate

    nombre = f"Equipo {mac[-5:]}"
    equipo_payload = EquipoCreate(nombre=nombre, mac_address=mac)

    try:
        equipo = create_equipo(db, equipo_payload)
    except IntegrityError:
        # Probablemente mac_address duplicada
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Equipo con esa MAC ya existe"
        )

    return equipo
