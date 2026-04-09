"""Servicios de generación de reportes descargables (CSV/PDF)."""

import csv
import re
import textwrap
import unicodedata
from datetime import datetime, timezone
from io import StringIO

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.mantencion import Mantencion
from app.services.dashboard_service import get_dashboard_summary

_INVISIBLE_CHARS_RE = re.compile(r"^[\u200E\u200F\u202A-\u202E\s\t]+")
_PDF_MAX_LINES = 45


def _build_filename(prefix: str, extension: str) -> str:
    """Genera un nombre de archivo con timestamp UTC."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def _format_datetime(value: datetime | None) -> str:
    """Formatea datetimes a ISO-8601 cuando existen."""

    if value is None:
        return ""
    return value.isoformat()


def _normalize_csv(content: str) -> str:
    """Agrega BOM UTF-8 para mejor compatibilidad con Excel."""

    return f"\ufeff{content}"


def _sanitize_csv_cell(value: object) -> object:
    """Neutraliza inyección de fórmulas en CSV para clientes tipo Excel."""

    if not isinstance(value, str) or not value:
        return value

    stripped = _INVISIBLE_CHARS_RE.sub("", value)
    if stripped and stripped[0] in ("=", "+", "-", "@", "\t"):
        return f"'{value}"

    return value


def _to_csv(headers: list[str], rows: list[list[object]]) -> str:
    """Renderiza una estructura tabular a CSV UTF-8."""

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([_sanitize_csv_cell(cell) for cell in row])
    return _normalize_csv(buffer.getvalue())


def _normalize_pdf_text(value: str) -> str:
    """Normaliza texto para PDF ASCII seguro."""

    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return ascii_value


def _escape_pdf_text(value: str) -> str:
    """Escapa caracteres reservados del formato PDF."""

    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines: list[str]) -> bytes:
    """Construye un PDF simple de una página con texto plano."""

    wrapped_lines: list[str] = []
    for line in lines:
        wrapped_lines.extend(textwrap.wrap(line, width=92) or [""])

    # A4 vertical: 595x842, línea de 16pt permite ~45 líneas útiles.
    # Si se excede el límite, se reserva la última línea para advertencia explícita.
    visible_lines = wrapped_lines
    if len(wrapped_lines) > _PDF_MAX_LINES:
        warning_line = (
            "[AVISO] Informe resumido por limite de pagina. Revisa CSV para detalle."
        )
        visible_lines = wrapped_lines[: _PDF_MAX_LINES - 1] + [warning_line]

    safe_lines = [_escape_pdf_text(_normalize_pdf_text(line)) for line in visible_lines]

    commands = ["BT", "/F1 12 Tf", "50 800 Td"]
    if safe_lines:
        commands.append(f"({safe_lines[0]}) Tj")
        for line in safe_lines[1:]:
            commands.append("0 -16 Td")
            commands.append(f"({line}) Tj")
    commands.append("ET")

    stream_data = "\n".join(commands).encode("latin-1", errors="ignore")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        (
            f"5 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("latin-1")
            + stream_data
            + b"\nendstream\nendobj\n"
        ),
    ]

    pdf = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets: list[int] = [0]

    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj

    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode("latin-1")

    pdf += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode("latin-1")

    return pdf


def export_lecturas_csv(
    db: Session,
    equipo_id: int | None = None,
    limit: int | None = 5000,
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> tuple[str, str]:
    """Genera exportable CSV de lecturas para análisis técnico."""

    query = (
        select(
            Lectura.id,
            Lectura.equipo_id,
            Equipo.nombre.label("equipo_nombre"),
            Lectura.temperatura,
            Lectura.humedad,
            Lectura.vib_x,
            Lectura.vib_y,
            Lectura.vib_z,
            Lectura.timestamp,
        )
        .join(Equipo, Equipo.id == Lectura.equipo_id)
        .order_by(Lectura.timestamp.desc(), Lectura.id.desc())
    )

    if equipo_id is not None:
        query = query.where(Lectura.equipo_id == equipo_id)
    if desde is not None:
        query = query.where(Lectura.timestamp >= desde)
    if hasta is not None:
        query = query.where(Lectura.timestamp <= hasta)
    if limit is not None:
        query = query.limit(limit)

    rows = db.execute(query).all()
    csv_content = _to_csv(
        headers=[
            "id",
            "equipo_id",
            "equipo_nombre",
            "temperatura",
            "humedad",
            "vib_x",
            "vib_y",
            "vib_z",
            "timestamp",
        ],
        rows=[
            [
                row.id,
                row.equipo_id,
                row.equipo_nombre,
                row.temperatura,
                row.humedad,
                row.vib_x,
                row.vib_y,
                row.vib_z,
                _format_datetime(row.timestamp),
            ]
            for row in rows
        ],
    )
    return _build_filename("manttoai_lecturas", "csv"), csv_content


def export_alertas_csv(
    db: Session,
    equipo_id: int | None = None,
    solo_no_leidas: bool = False,
    limit: int | None = 5000,
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> tuple[str, str]:
    """Genera exportable CSV de alertas para auditoría operativa."""

    query = (
        select(
            Alerta.id,
            Alerta.equipo_id,
            Equipo.nombre.label("equipo_nombre"),
            Alerta.tipo,
            Alerta.mensaje,
            Alerta.nivel,
            Alerta.leida,
            Alerta.email_enviado,
            Alerta.created_at,
        )
        .join(Equipo, Equipo.id == Alerta.equipo_id)
        .order_by(Alerta.created_at.desc(), Alerta.id.desc())
    )

    if equipo_id is not None:
        query = query.where(Alerta.equipo_id == equipo_id)
    if solo_no_leidas:
        query = query.where(Alerta.leida.is_(False))
    if desde is not None:
        query = query.where(Alerta.created_at >= desde)
    if hasta is not None:
        query = query.where(Alerta.created_at <= hasta)
    if limit is not None:
        query = query.limit(limit)

    rows = db.execute(query).all()
    csv_content = _to_csv(
        headers=[
            "id",
            "equipo_id",
            "equipo_nombre",
            "tipo",
            "mensaje",
            "nivel",
            "leida",
            "email_enviado",
            "created_at",
        ],
        rows=[
            [
                row.id,
                row.equipo_id,
                row.equipo_nombre,
                row.tipo,
                row.mensaje,
                row.nivel,
                row.leida,
                row.email_enviado,
                _format_datetime(row.created_at),
            ]
            for row in rows
        ],
    )
    return _build_filename("manttoai_alertas", "csv"), csv_content


def export_mantenciones_csv(
    db: Session,
    equipo_id: int | None = None,
    limit: int | None = 5000,
    order: str = "desc",
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> tuple[str, str]:
    """Genera exportable CSV de mantenciones para trazabilidad."""

    query = select(
        Mantencion.id,
        Mantencion.equipo_id,
        Equipo.nombre.label("equipo_nombre"),
        Mantencion.tipo,
        Mantencion.descripcion,
        Mantencion.estado,
        Mantencion.fecha_programada,
        Mantencion.fecha_ejecucion,
        Mantencion.created_at,
    ).join(Equipo, Equipo.id == Mantencion.equipo_id)

    if equipo_id is not None:
        query = query.where(Mantencion.equipo_id == equipo_id)
    if desde is not None:
        query = query.where(Mantencion.created_at >= desde)
    if hasta is not None:
        query = query.where(Mantencion.created_at <= hasta)

    if order.lower() == "asc":
        query = query.order_by(Mantencion.created_at.asc(), Mantencion.id.asc())
    else:
        query = query.order_by(Mantencion.created_at.desc(), Mantencion.id.desc())

    if limit is not None:
        query = query.limit(limit)

    rows = db.execute(query).all()
    csv_content = _to_csv(
        headers=[
            "id",
            "equipo_id",
            "equipo_nombre",
            "tipo",
            "descripcion",
            "estado",
            "fecha_programada",
            "fecha_ejecucion",
            "created_at",
        ],
        rows=[
            [
                row.id,
                row.equipo_id,
                row.equipo_nombre,
                row.tipo,
                row.descripcion,
                row.estado,
                _format_datetime(row.fecha_programada),
                _format_datetime(row.fecha_ejecucion),
                _format_datetime(row.created_at),
            ]
            for row in rows
        ],
    )
    return _build_filename("manttoai_mantenciones", "csv"), csv_content


def export_informe_ejecutivo_pdf(
    db: Session,
    desde: datetime | None = None,
    hasta: datetime | None = None,
) -> tuple[str, bytes]:
    """Genera informe ejecutivo PDF para stakeholders no técnicos."""

    summary = get_dashboard_summary(db)
    now = datetime.now(timezone.utc)

    lecturas_count_query = select(func.count(Lectura.id))
    alertas_count_query = select(func.count(Alerta.id))
    mantenciones_count_query = select(func.count(Mantencion.id))

    if desde is not None:
        lecturas_count_query = lecturas_count_query.where(Lectura.timestamp >= desde)
        alertas_count_query = alertas_count_query.where(Alerta.created_at >= desde)
        mantenciones_count_query = mantenciones_count_query.where(
            Mantencion.created_at >= desde
        )

    if hasta is not None:
        lecturas_count_query = lecturas_count_query.where(Lectura.timestamp <= hasta)
        alertas_count_query = alertas_count_query.where(Alerta.created_at <= hasta)
        mantenciones_count_query = mantenciones_count_query.where(
            Mantencion.created_at <= hasta
        )

    lecturas_count = int(db.scalar(lecturas_count_query) or 0)
    alertas_count = int(db.scalar(alertas_count_query) or 0)
    mantenciones_count = int(db.scalar(mantenciones_count_query) or 0)

    equipos_ordenados = sorted(
        summary.get("equipos", []),
        key=lambda equipo: float(equipo.get("ultima_probabilidad") or 0.0),
        reverse=True,
    )

    periodo_label = (
        f"{_format_datetime(desde)} a {_format_datetime(hasta)}"
        if (desde or hasta)
        else "historico completo"
    )

    lines = [
        "Informe Ejecutivo ManttoAI",
        f"Generado: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Periodo analizado: {periodo_label}",
        "",
        "Resumen KPI:",
        f"- Equipos monitoreados: {summary.get('total_equipos', 0)}",
        f"- Alertas activas: {summary.get('alertas_activas', 0)}",
        f"- Equipos en riesgo: {summary.get('equipos_en_riesgo', 0)}",
        f"- Ultima clasificacion global: {summary.get('ultima_clasificacion', 'sin datos')}",
        f"- Probabilidad de falla global: {float(summary.get('probabilidad_falla', 0.0)):.2%}",
        "",
        "Volumen de registros en el periodo:",
        f"- Lecturas: {lecturas_count}",
        f"- Alertas: {alertas_count}",
        f"- Mantenciones: {mantenciones_count}",
        "",
        "Top equipos por probabilidad de falla:",
    ]

    if equipos_ordenados:
        for equipo in equipos_ordenados[:5]:
            probabilidad = float(equipo.get("ultima_probabilidad") or 0.0)
            alertas_activas = int(equipo.get("alertas_activas") or 0)
            lines.append(
                f"- {equipo.get('nombre', 'Equipo')} | Riesgo {probabilidad:.2%} | Alertas activas {alertas_activas}"
            )
    else:
        lines.append("- Sin datos suficientes para ranking de riesgo")

    lines.extend(
        [
            "",
            "Recomendacion operativa:",
            "- Priorizar intervencion de equipos con riesgo >= 50%.",
            "- Mantener ciclo de exportes CSV semanales para trazabilidad.",
        ]
    )

    return _build_filename("manttoai_informe_ejecutivo", "pdf"), _build_simple_pdf(
        lines
    )
