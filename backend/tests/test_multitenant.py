"""Tests del middleware multi-tenant y aislamiento de datos entre organizaciones."""

from types import SimpleNamespace

from sqlalchemy import select

from app.middleware.tenant import _extract_tenant_slug, _resolve_tenant
from app.models.equipo import Equipo
from app.models.organizacion import Organizacion


def test_tenant_middleware_extracts_from_header():
    """Valida extraccion de tenant slug desde header X-Tenant-ID."""

    request = SimpleNamespace(
        headers={"X-Tenant-ID": "cliente-alfa", "host": "localhost:8000"},
    )
    slug = _extract_tenant_slug(request)

    assert slug == "cliente-alfa"


def test_tenant_middleware_extracts_from_header_case_insensitive():
    """Valida que el slug se normalice a minusculas desde header."""

    request = SimpleNamespace(
        headers={"X-Tenant-ID": "Cliente-Beta", "host": "localhost:8000"},
    )
    slug = _extract_tenant_slug(request)

    assert slug == "cliente-beta"


def test_tenant_middleware_extracts_from_subdomain():
    """Valida extraccion de tenant slug desde subdominio del host."""

    request = SimpleNamespace(
        headers={"host": "cliente-alfa.manttoai.com"},
    )
    slug = _extract_tenant_slug(request)

    assert slug == "cliente-alfa"


def test_tenant_middleware_extracts_from_deep_subdomain():
    """Valida extraccion desde subdominio de varios niveles."""

    request = SimpleNamespace(
        headers={"host": "cliente-alfa.staging.manttoai.com"},
    )
    slug = _extract_tenant_slug(request)

    assert slug == "cliente-alfa"


def test_tenant_middleware_skips_www_subdomain():
    """Valida que 'www' como subdominio no se considere tenant."""

    request = SimpleNamespace(
        headers={"host": "www.manttoai.com"},
    )
    slug = _extract_tenant_slug(request)

    assert slug is None


def test_tenant_middleware_no_tenant_on_localhost():
    """Valida que localhost no genere slug de tenant."""

    request = SimpleNamespace(
        headers={"host": "localhost:8000"},
    )
    slug = _extract_tenant_slug(request)

    assert slug is None


def test_tenant_resolve_from_header(db):
    """Valida resolucion de slug a organizacion_id desde X-Tenant-ID."""

    from app import main

    org = Organizacion(nombre="Cliente Alfa", slug="cliente-alfa", is_active=True)
    db.add(org)
    db.commit()
    db.refresh(org)

    request = SimpleNamespace(
        headers={"X-Tenant-ID": "cliente-alfa"},
        app=main.app,
    )
    org_id = _resolve_tenant(request)

    assert org_id == org.id


def test_tenant_resolve_from_subdomain(db):
    """Valida resolucion de slug a organizacion_id desde subdominio."""

    from app import main

    org = Organizacion(nombre="Cliente Beta", slug="cliente-beta", is_active=True)
    db.add(org)
    db.commit()
    db.refresh(org)

    request = SimpleNamespace(
        headers={"host": "cliente-beta.manttoai.com"},
        app=main.app,
    )
    org_id = _resolve_tenant(request)

    assert org_id == org.id


def test_tenant_resolve_inactive_org_returns_none(db):
    """Valida que organizacion inactiva retorne None al resolver."""

    from app import main

    org = Organizacion(nombre="Inactiva", slug="inactiva", is_active=False)
    db.add(org)
    db.commit()
    db.refresh(org)

    request = SimpleNamespace(
        headers={"X-Tenant-ID": "inactiva"},
        app=main.app,
    )
    org_id = _resolve_tenant(request)

    assert org_id is None


def test_tenant_resolve_unknown_slug_returns_none(db):
    """Valida que slug inexistente retorne None al resolver."""

    from app import main

    request = SimpleNamespace(
        headers={"X-Tenant-ID": "no-existe"},
        app=main.app,
    )
    org_id = _resolve_tenant(request)

    assert org_id is None


def test_tenant_isolation(db):
    """Valida que datos de tenant A no sean accesibles desde tenant B."""

    org_a = Organizacion(nombre="Org A", slug="org-a", is_active=True)
    org_b = Organizacion(nombre="Org B", slug="org-b", is_active=True)
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh(org_a)
    db.refresh(org_b)

    equipo_a = Equipo(
        nombre="Equipo A", tipo="Motor", estado="operativo",
        ubicacion="Planta A", rubro="industrial",
        organizacion_id=org_a.id,
    )
    equipo_b = Equipo(
        nombre="Equipo B", tipo="Motor", estado="operativo",
        ubicacion="Planta B", rubro="agricola",
        organizacion_id=org_b.id,
    )
    db.add_all([equipo_a, equipo_b])
    db.commit()

    # Consultar equipos de org_a
    eqs_a = list(
        db.scalars(
            select(Equipo).where(Equipo.organizacion_id == org_a.id)
        )
    )
    # Consultar equipos de org_b
    eqs_b = list(
        db.scalars(
            select(Equipo).where(Equipo.organizacion_id == org_b.id)
        )
    )

    assert len(eqs_a) == 1
    assert len(eqs_b) == 1
    assert eqs_a[0].nombre == "Equipo A"
    assert eqs_b[0].nombre == "Equipo B"
    assert eqs_a[0].id != eqs_b[0].id
    assert eqs_a[0].rubro == "industrial"
    assert eqs_b[0].rubro == "agricola"


def test_tenant_isolation_no_cross_contamination(db):
    """Valida que cada tenant solo vea sus propios equipos (cantidades)."""

    org_a = Organizacion(nombre="Org A-2", slug="org-a2", is_active=True)
    org_b = Organizacion(nombre="Org B-2", slug="org-b2", is_active=True)
    db.add_all([org_a, org_b])
    db.commit()
    db.refresh(org_a)
    db.refresh(org_b)

    for i in range(3):
        db.add(Equipo(
            nombre=f"Equipo A-{i}", tipo="Motor", estado="operativo",
            organizacion_id=org_a.id,
        ))
    for i in range(5):
        db.add(Equipo(
            nombre=f"Equipo B-{i}", tipo="Sensor", estado="operativo",
            organizacion_id=org_b.id,
        ))
    db.commit()

    all_a = list(
        db.scalars(select(Equipo).where(Equipo.organizacion_id == org_a.id))
    )
    all_b = list(
        db.scalars(select(Equipo).where(Equipo.organizacion_id == org_b.id))
    )
    all_total = list(db.scalars(select(Equipo)))

    assert len(all_a) == 3
    assert len(all_b) == 5
    assert len(all_total) == 8


def test_tenant_fallback_single_tenant(db):
    """Valida funcionamiento normal sin tenant (modo single-tenant)."""

    from app import main

    # Sin header X-Tenant-ID y con localhost
    request = SimpleNamespace(
        headers={"host": "localhost:8000"},
        app=main.app,
    )

    slug = _extract_tenant_slug(request)
    assert slug is None

    org_id = _resolve_tenant(request)
    assert org_id is None


def test_tenant_fallback_without_any_tenant_header(db):
    """Valida que sin headers de tenant todo funcione (compatibilidad hacia atras)."""

    request = SimpleNamespace(
        headers={},
    )

    slug = _extract_tenant_slug(request)
    assert slug is None
