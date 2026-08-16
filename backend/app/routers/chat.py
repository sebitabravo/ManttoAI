"""Router para el Chat de Asistencia."""

import json

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.dependencies import get_current_user, get_db, require_role
from app.models.chat import MensajeChat
from app.models.usuario import Usuario
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.services.chat_service import procesar_mensaje
from app.services.tenant_scope import add_organization_scope

router = APIRouter(prefix="/chat", tags=["chat"])


def _persist_chat_message(
    db: Session,
    user_id: int,
    mensaje_usuario: str,
    respuesta_ia: str,
    fuente: str,
) -> None:
    """Persiste un mensaje sin ejecutar SQL síncrono en el event loop."""

    db.add(
        MensajeChat(
            usuario_id=user_id,
            mensaje_usuario=mensaje_usuario,
            respuesta_ia=respuesta_ia,
            fuente=fuente,
        )
    )
    db.commit()


def _build_dataset_export(db: Session) -> str:
    """Construye el JSONL acotado fuera del event loop."""

    mensajes = db.scalars(
        add_organization_scope(
            select(MensajeChat).join(Usuario, Usuario.id == MensajeChat.usuario_id),
            Usuario.organizacion_id,
            db,
        )
        .order_by(MensajeChat.id.asc())
        .limit(10_000)
    )
    lines = []
    for msg in mensajes.yield_per(100):
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": "Eres el Asistente de Monitoreo IoT de ManttoAI. Ayudas a operadores a interpretar datos de sensores, entender alertas y tomar decisiones de mantenimiento basadas en la telemetría de sus equipos.",
                },
                {"role": "user", "content": msg.mensaje_usuario},
                {"role": "assistant", "content": msg.respuesta_ia},
            ]
        }
        lines.append(json.dumps(conversation, ensure_ascii=False))

    return "\n".join(lines)


def _list_chat_history(db: Session, skip: int, limit: int) -> list[MensajeChat]:
    """Lista historial administrativo fuera del event loop."""

    query = add_organization_scope(
        select(MensajeChat).join(Usuario, Usuario.id == MensajeChat.usuario_id),
        Usuario.organizacion_id,
        db,
    )
    return list(
        db.scalars(
            query.order_by(MensajeChat.fecha_creacion.desc()).offset(skip).limit(limit)
        ).all()
    )


@router.post("", response_model=ChatMessageResponse)
@router.post("/", response_model=ChatMessageResponse, include_in_schema=False)
async def chat_con_asistente(
    payload: ChatMessageRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatMessageResponse:
    """Envía un mensaje al asistente híbrido (Reglas + IA) y guarda el historial."""
    resultado = await procesar_mensaje(payload.mensaje, db)

    await run_in_threadpool(
        _persist_chat_message,
        db,
        current_user.id,
        payload.mensaje,
        resultado["respuesta"],
        resultado["fuente"],
    )

    return ChatMessageResponse(
        respuesta=resultado["respuesta"], fuente=resultado["fuente"]
    )


@router.get("/dataset-export")
async def exportar_dataset(
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> Response:
    """
    Exporta el historial en formato JSONL compatible con OpenAI/ChatML para futuro Fine-Tuning.
    """
    content = await run_in_threadpool(_build_dataset_export, db)

    return Response(
        content=content,
        media_type="application/x-ndjson",
        headers={"Content-Disposition": 'attachment; filename="dataset.jsonl"'},
    )


@router.get("/historial", response_model=list[ChatHistoryResponse])
async def obtener_historial(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> list[MensajeChat]:
    """Obtiene el historial de chat de todos los usuarios (Solo Admin)."""
    return await run_in_threadpool(_list_chat_history, db, skip, limit)
