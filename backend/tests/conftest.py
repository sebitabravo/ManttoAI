"""Fixtures compartidas para pytest."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.dependencies import get_db
from app import main
from app.models.usuario import Usuario
from app.middleware.rate_limit import limiter
from app.services.auth_service import create_access_token, hash_password

@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Resetea el rate limiter en memoria antes de cada test."""

    storage = getattr(limiter, "_storage", None)
    if storage is not None and hasattr(storage, "reset"):
        storage.reset()
    elif storage is not None and hasattr(storage, "clear"):
        storage.clear()


TEST_USER_EMAIL = "admin@manttoai.local"
TEST_USER_PASSWORD = "Admin123!"
TEST_USER_NAME = "Admin ManttoAI"
TEST_TECNICO_EMAIL = "tecnico@manttoai.local"
TEST_TECNICO_PASSWORD = "Tecnico123!"
TEST_TECNICO_NAME = "Tecnico ManttoAI"


def _build_client(authenticated: bool) -> Generator[TestClient, None, None]:
    """Crea un cliente de pruebas opcionalmente autenticado."""

    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    with testing_session_local() as db:
        db.add(
            Usuario(
                nombre=TEST_USER_NAME,
                email=TEST_USER_EMAIL,
                password_hash=hash_password(TEST_USER_PASSWORD),
                rol="admin",
            )
        )
        db.commit()

    previous_database_auto_init = main.settings.database_auto_init
    previous_mqtt_enabled = main.settings.mqtt_enabled
    previous_prediction_scheduler = main.settings.enable_prediction_scheduler
    previous_database_url = main.settings.database_url

    main.settings.database_auto_init = False
    main.settings.mqtt_enabled = False
    main.settings.enable_prediction_scheduler = False
    main.settings.database_url = "sqlite:///:memory:"
    main.app.dependency_overrides[get_db] = override_get_db
    main.app.state.testing_session_local = testing_session_local

    token = create_access_token(TEST_USER_EMAIL)

    with TestClient(main.app) as test_client:
        if authenticated:
            test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client

    main.app.dependency_overrides.pop(get_db, None)
    if hasattr(main.app.state, "testing_session_local"):
        delattr(main.app.state, "testing_session_local")
    main.settings.database_auto_init = previous_database_auto_init
    main.settings.mqtt_enabled = previous_mqtt_enabled
    main.settings.enable_prediction_scheduler = previous_prediction_scheduler
    main.settings.database_url = previous_database_url
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Entrega cliente autenticado para tests de endpoints operativos."""

    yield from _build_client(authenticated=True)


@pytest.fixture
def unauthenticated_client() -> Generator[TestClient, None, None]:
    """Entrega cliente sin token para validar rechazo de endpoints protegidos."""

    yield from _build_client(authenticated=False)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Entrega sesión aislada y configura overrides de app para tests de routers."""

    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db_session = testing_session_local()
        try:
            yield db_session
        finally:
            db_session.close()

    previous_database_auto_init = main.settings.database_auto_init
    previous_mqtt_enabled = main.settings.mqtt_enabled
    previous_prediction_scheduler = main.settings.enable_prediction_scheduler
    previous_database_url = main.settings.database_url

    main.settings.database_auto_init = False
    main.settings.mqtt_enabled = False
    main.settings.enable_prediction_scheduler = False
    main.settings.database_url = "sqlite:///:memory:"
    main.app.dependency_overrides[get_db] = override_get_db
    main.app.state.testing_session_local = testing_session_local

    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        main.app.dependency_overrides.pop(get_db, None)
        if hasattr(main.app.state, "testing_session_local"):
            delattr(main.app.state, "testing_session_local")
        main.settings.database_auto_init = previous_database_auto_init
        main.settings.mqtt_enabled = previous_mqtt_enabled
        main.settings.enable_prediction_scheduler = previous_prediction_scheduler
        main.settings.database_url = previous_database_url
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def admin_user(db: Session) -> Usuario:
    """Entrega usuario admin persistido para tests de servicios/routers."""

    existing = db.scalars(
        select(Usuario).where(Usuario.email == TEST_USER_EMAIL)
    ).first()
    if existing:
        return existing

    usuario = Usuario(
        nombre=TEST_USER_NAME,
        email=TEST_USER_EMAIL,
        password_hash=hash_password(TEST_USER_PASSWORD),
        rol="admin",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def tecnico_user(db: Session) -> Usuario:
    """Entrega usuario técnico persistido para tests RBAC."""

    existing = db.scalars(
        select(Usuario).where(Usuario.email == TEST_TECNICO_EMAIL)
    ).first()
    if existing:
        return existing

    usuario = Usuario(
        nombre=TEST_TECNICO_NAME,
        email=TEST_TECNICO_EMAIL,
        password_hash=hash_password(TEST_TECNICO_PASSWORD),
        rol="tecnico",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def admin_token(admin_user: Usuario) -> str:
    """Entrega JWT válido para usuario admin de tests."""

    return create_access_token(admin_user.email)


@pytest.fixture
def tecnico_token(tecnico_user: Usuario) -> str:
    """Entrega JWT válido para usuario técnico de tests."""

    return create_access_token(tecnico_user.email)
