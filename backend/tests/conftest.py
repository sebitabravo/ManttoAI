"""Fixtures compartidas para pytest."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.database import Base
from app.dependencies import get_db
from app import main


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Entrega un cliente de prueba con base de datos aislada en memoria."""

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

    previous_database_auto_init = main.settings.database_auto_init
    previous_mqtt_enabled = main.settings.mqtt_enabled
    previous_prediction_scheduler = main.settings.enable_prediction_scheduler

    main.settings.database_auto_init = False
    main.settings.mqtt_enabled = False
    main.settings.enable_prediction_scheduler = False
    main.app.dependency_overrides[get_db] = override_get_db

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.pop(get_db, None)
    main.settings.database_auto_init = previous_database_auto_init
    main.settings.mqtt_enabled = previous_mqtt_enabled
    main.settings.enable_prediction_scheduler = previous_prediction_scheduler
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
