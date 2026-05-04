"""Router para el Chat de Asistencia."""

from typing import List

import json

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_role
from app.models.chat import MensajeChat
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.services.chat_service import procesar_mensaje

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatMessageResponse)
@router.post("/", response_model=ChatMessageResponse, include_in_schema=False)
async def chat_con_asistente(
    payload: ChatMessageRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Envía un mensaje al asistente híbrido (Reglas + IA) y guarda el historial."""
    resultado = await procesar_mensaje(payload.mensaje, db)

    # Persistir el mensaje en el historial
    nuevo_mensaje = MensajeChat(
        usuario_id=current_user.id,
        mensaje_usuario=payload.mensaje,
        respuesta_ia=resultado["respuesta"],
        fuente=resultado["fuente"],
    )
    db.add(nuevo_mensaje)
    db.commit()

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
    mensajes = db.query(MensajeChat).order_by(MensajeChat.id.asc()).all()
    lines = []
    for msg in mensajes:
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

    return Response(
        content="\n".join(lines),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": 'attachment; filename="dataset.jsonl"'},
    )


@router.get("/historial", response_model=List[ChatHistoryResponse])
async def obtener_historial(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> list[MensajeChat]:
    """Obtiene el historial de chat de todos los usuarios (Solo Admin)."""
    mensajes = (
        db.query(MensajeChat)
        .order_by(MensajeChat.fecha_creacion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return mensajes
