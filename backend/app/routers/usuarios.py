"""Endpoints de gestión de usuarios (solo admin)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.models.audit_log import AuditLog
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioListResponse,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.services.auth_service import register_user

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=UsuarioListResponse)
@limiter.limit("100/hour")
def list_usuarios(
    request: Request,
    rol: str | None = Query(None, description="Filtrar por rol"),
    is_active: bool | None = Query(None, description="Filtrar por estado activo"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(50, ge=1, le=100, description="Resultados por página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> UsuarioListResponse:
    """Lista todos los usuarios con filtros opcionales (solo admin)."""

    query = select(Usuario)

    if rol:
        query = query.where(Usuario.rol == rol)

    if is_active is not None:
        query = query.where(Usuario.is_active == is_active)

    # Contar total usando COUNT(*) - O(1) en la DB
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Aplicar paginación
    query = query.order_by(Usuario.created_at.desc())
    query = query.limit(per_page).offset((page - 1) * per_page)

    usuarios = list(db.scalars(query).all())

    return UsuarioListResponse(
        usuarios=[UsuarioResponse.model_validate(u) for u in usuarios],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
@limiter.limit("200/hour")
def get_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> UsuarioResponse:
    """Retorna un usuario por ID (solo admin)."""

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return UsuarioResponse.model_validate(usuario)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Crear usuarios es más sensible
def create_usuario(
    payload: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> UsuarioResponse:
    """Crea un nuevo usuario (solo admin)."""

    try:
        return register_user(db, payload)
    except HTTPException as e:
        if e.status_code == status.HTTP_409_CONFLICT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail,
            ) from e
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.put("/{usuario_id}", response_model=UsuarioResponse)
@limiter.limit("50/hour")
def update_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> UsuarioResponse:
    """Actualiza un usuario (solo admin)."""

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Actualizar campos proporcionados
    if payload.nombre is not None:
        usuario.nombre = payload.nombre
    if payload.email is not None:
        # Verificar que email no exista
        existing = db.scalars(
            select(Usuario).where(
                Usuario.email == payload.email, Usuario.id != usuario_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya en uso"
            )
        usuario.email = payload.email
    if payload.rol is not None:
        usuario.rol = payload.rol
    if payload.is_active is not None:
        usuario.is_active = payload.is_active

    db.commit()
    db.refresh(usuario)

    return UsuarioResponse.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/hour")  # Eliminar usuarios es muy sensible
def delete_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> None:
    """Elimina un usuario (solo admin)."""

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Prevenir que un admin se elimine a sí mismo
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario",
        )

    db.delete(usuario)
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints RGPD — Derecho al olvido y portabilidad de datos (RN-02)
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/{usuario_id}/exportar-datos")
@limiter.limit("10/hour")
def exportar_datos_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> dict:
    """
    Exporta todos los datos personales de un usuario en formato portátil (RGPD Art. 20).

    Incluye: datos de cuenta, equipos asociados, audit logs.
    Permite al usuario ejercer su derecho de portabilidad de datos.
    """
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Recopilar audit logs del usuario
    audit_logs = list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.usuario_id == usuario_id)
            .order_by(AuditLog.created_at.desc())
            .limit(500)
        )
    )

    return {
        "exportado_en": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "titular": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
            "is_active": usuario.is_active,
            "created_at": usuario.created_at.isoformat()
            if usuario.created_at
            else None,
        },
        "audit_logs": [
            {
                "id": log.id,
                "accion": log.action,
                "entidad": log.entity_type,
                "entidad_id": log.entity_id,
                "ip": log.ip_address,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_logs
        ],
        "nota_legal": (
            "Exportación generada en cumplimiento del derecho de portabilidad "
            "de datos (Ley 19.628 Art. 12 / RGPD Art. 20). "
            "Los datos de telemetría de equipos no se incluyen por ser datos "
            "industriales no personales."
        ),
    }


@router.delete("/{usuario_id}/datos-personales", status_code=status.HTTP_200_OK)
@limiter.limit("5/hour")
def eliminar_datos_personales(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> dict:
    """
    Elimina o anonimiza todos los datos personales de un usuario (RGPD Art. 17 / Ley 19.628).

    Implementa el derecho al olvido:
    - Anonimiza nombre y email del usuario (no elimina el registro para mantener integridad referencial)
    - Elimina audit logs asociados al usuario
    - Desactiva la cuenta permanentemente

    Los datos de telemetría (lecturas, alertas, predicciones) se mantienen
    porque son datos industriales del equipo, no datos personales del usuario.
    """
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Prevenir auto-eliminación
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tus propios datos personales",
        )

    # Anonimizar datos personales (preserva integridad referencial)
    email_anonimizado = f"eliminado_{usuario_id}@anonimizado.manttoai"
    usuario.nombre = f"Usuario Eliminado #{usuario_id}"
    usuario.email = email_anonimizado
    usuario.password_hash = "ELIMINADO"
    usuario.is_active = False

    # Eliminar audit logs del usuario (datos de comportamiento personal)
    db.execute(delete(AuditLog).where(AuditLog.usuario_id == usuario_id))

    db.commit()

    return {
        "mensaje": "Datos personales eliminados correctamente",
        "usuario_id": usuario_id,
        "email_anonimizado": email_anonimizado,
        "eliminado_en": datetime.now(timezone.utc).isoformat(),
        "nota_legal": (
            "Datos personales anonimizados en cumplimiento del derecho al olvido "
            "(Ley 19.628 / RGPD Art. 17). El registro se mantiene anonimizado "
            "para preservar la integridad referencial del sistema."
        ),
    }
