"""Crea un administrador local sin credenciales embebidas."""

import getpass
import os

from app.config import NON_DEV_ENVS
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.services.auth_service import hash_password


def main() -> None:
    """Crea o actualiza un admin únicamente en entornos locales."""

    app_env = os.getenv("APP_ENV", "development").strip().lower()
    if app_env in NON_DEV_ENVS:
        raise SystemExit(
            "Abortado: create_admin.py solo puede ejecutarse en development/local."
        )

    email = os.getenv("ADMIN_EMAIL", "").strip() or input("Email admin: ").strip()
    nombre = os.getenv("ADMIN_NAME", "").strip() or input("Nombre admin: ").strip()
    password = os.getenv("ADMIN_PASSWORD", "") or getpass.getpass(
        "Contraseña admin (no se mostrará): "
    )
    payload = UsuarioCreate(
        nombre=nombre,
        email=email,
        password=password,
        rol="admin",
    )

    with SessionLocal() as db:
        usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
        if usuario is None:
            usuario = Usuario(
                nombre=payload.nombre,
                email=payload.email,
                password_hash=hash_password(payload.password),
                rol="admin",
            )
            db.add(usuario)
        else:
            usuario.nombre = payload.nombre
            usuario.rol = "admin"
            usuario.password_hash = hash_password(payload.password)
            usuario.is_active = True
        db.commit()

    print(f"Administrador preparado: {payload.email}")


if __name__ == "__main__":
    main()
