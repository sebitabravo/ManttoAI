"""Endpoints de exportación de reportes (CSV y PDF)."""

from datetime import datetime
import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limit_by_role
from app.services.report_service import (
    export_alertas_csv,
    export_informe_ejecutivo_pdf,
    export_lecturas_csv,
    export_mantenciones_csv,
)

router = APIRouter(prefix="/reportes", tags=["reportes"])
_SANITIZE_HEADER_VALUE_RE = re.compile(r"[\r\n\"]+")


def _validate_date_range(desde: datetime | None, hasta: datetime | None) -> None:
    """Valida que el rango de fechas sea consistente."""

    if not (desde and hasta):
        return

    try:
        invalid_range = desde > hasta
    except TypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Rango de fechas inválido: formatos de zona horaria incompatibles. "
                "Usá ambos timestamps con zona horaria (ej: 2026-04-08T00:00:00Z)."
            ),
        ) from exc

    if invalid_range:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rango de fechas inválido: 'desde' debe ser menor o igual que 'hasta'.",
        )


def _content_disposition_attachment(filename: str) -> str:
    """Construye Content-Disposition seguro y compatible (RFC5987)."""

    safe_ascii = "".join(char for char in filename if ord(char) < 128)
    safe_ascii = _SANITIZE_HEADER_VALUE_RE.sub("", safe_ascii)
    if not safe_ascii:
        safe_ascii = "reporte"

    encoded_filename = quote(filename, safe="")
    return f"attachment; filename=\"{safe_ascii}\"; filename*=UTF-8''{encoded_filename}"


@router.get(
    "/lecturas.csv",
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limit_by_role(
    admin_limit="80/hour",
    tecnico_limit="60/hour",
    visualizador_limit="40/hour",
)
def get_lecturas_csv(
    request: Request,
    equipo_id: int | None = Query(default=None),
    limit: int = Query(default=5000, ge=1, le=20000),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Descarga lecturas en formato CSV."""

    _validate_date_range(desde, hasta)
    filename, csv_content = export_lecturas_csv(
        db,
        equipo_id=equipo_id,
        limit=limit,
        desde=desde,
        hasta=hasta,
    )
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": _content_disposition_attachment(filename),
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/alertas.csv",
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limit_by_role(
    admin_limit="80/hour",
    tecnico_limit="60/hour",
    visualizador_limit="40/hour",
)
def get_alertas_csv(
    request: Request,
    equipo_id: int | None = Query(default=None),
    solo_no_leidas: bool = Query(default=False),
    limit: int = Query(default=5000, ge=1, le=20000),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Descarga alertas en formato CSV."""

    _validate_date_range(desde, hasta)
    filename, csv_content = export_alertas_csv(
        db,
        equipo_id=equipo_id,
        solo_no_leidas=solo_no_leidas,
        limit=limit,
        desde=desde,
        hasta=hasta,
    )
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": _content_disposition_attachment(filename),
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/mantenciones.csv",
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limit_by_role(
    admin_limit="80/hour",
    tecnico_limit="60/hour",
    visualizador_limit="40/hour",
)
def get_mantenciones_csv(
    request: Request,
    equipo_id: int | None = Query(default=None),
    limit: int = Query(default=5000, ge=1, le=20000),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Descarga mantenciones en formato CSV."""

    _validate_date_range(desde, hasta)
    filename, csv_content = export_mantenciones_csv(
        db,
        equipo_id=equipo_id,
        limit=limit,
        order=order,
        desde=desde,
        hasta=hasta,
    )
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": _content_disposition_attachment(filename),
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/ejecutivo.pdf",
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limit_by_role(
    admin_limit="40/hour",
    tecnico_limit="30/hour",
    visualizador_limit="20/hour",
)
def get_informe_ejecutivo_pdf(
    request: Request,
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Descarga informe ejecutivo en PDF para stakeholders."""

    _validate_date_range(desde, hasta)
    filename, pdf_content = export_informe_ejecutivo_pdf(
        db,
        desde=desde,
        hasta=hasta,
    )
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": _content_disposition_attachment(filename),
            "Cache-Control": "no-store",
        },
    )
