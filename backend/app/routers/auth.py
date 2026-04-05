"""Endpoints de autenticación."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
def register(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    """Registra un usuario persistido."""

    return register_user(db, payload)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Retorna un token JWT para credenciales válidas."""

    return login_user(db, payload.email, payload.password)
