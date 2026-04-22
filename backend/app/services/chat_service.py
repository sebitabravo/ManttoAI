"""Servicio del Asistente de Mantenimiento Híbrido."""

import httpx
import logging
from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.dashboard_service import get_dashboard_summary

logger = logging.getLogger(__name__)
settings = get_settings()

# Diccionario de reglas simples para respuestas instantáneas
REGLAS_MANTENIMIENTO = {
    "temperatura": "La alta temperatura suele deberse a falta de lubricación o fricción en rodamientos. Sugiero revisar el nivel de aceite y la ventilación del equipo.",
    "vibracion": "Una vibración inusual (valores mayores a 0.5 G) puede indicar desalineación, desbalanceo o desgaste en los rodamientos. Detén el equipo si supera 1.0 G.",
    "vibración": "Una vibración inusual (valores mayores a 0.5 G) puede indicar desalineación, desbalanceo o desgaste en los rodamientos. Detén el equipo si supera 1.0 G.",
    "grafico": "Los gráficos de temperatura y vibración te permiten ver tendencias en tiempo real y históricas. Detectan cambios anormales antes de que ocurra una falla, permitiéndote actuar preventivamente.",
    "gráfico": "Los gráficos de temperatura y vibración te permiten ver tendencias en tiempo real y históricas. Detectan cambios anormales antes de que ocurra una falla, permitiéndote actuar preventivamente.",
    "bomba": "En bombas centrífugas, revisa que no haya cavitación (burbujas en el fluido) o filtros obstruidos si hay alertas de presión o ruido.",
    "motor": "Para motores eléctricos, verifica el estado del devanado y posibles cortocircuitos si notas picos de consumo o temperatura alta.",
    "alerta": "Si hay una alerta activa, revisa en el panel de telemetría qué métrica (temperatura o vibración) superó el umbral. Puedes silenciarla desde el panel de control.",
    "mantenimiento": "Recuerda registrar cada intervención en el historial del equipo. El mantenimiento preventivo regular incluye limpieza, lubricación y ajuste de piezas.",
    "dashboard": "El dashboard muestra el estado general de la planta: equipos activos, alertas en tiempo real, gráficos de temperatura y vibración, probabilidad de falla, e historial de mantenimiento. Es tu pantalla central de control.",
    "probabilidad": "La probabilidad de falla es una predicción (0 a 1). 0-0.3 = bajo riesgo (verde), 0.3-0.7 = moderado (amarillo), 0.7-1.0 = alto riesgo (rojo). Actúa según la urgencia.",
    "falla": "La probabilidad de falla es una predicción (0 a 1). 0-0.3 = bajo riesgo (verde), 0.3-0.7 = moderado (amarillo), 0.7-1.0 = alto riesgo (rojo). Actúa según la urgencia.",
    "riesgo": "La probabilidad de falla es una predicción (0 a 1). 0-0.3 = bajo riesgo (verde), 0.3-0.7 = moderado (amarillo), 0.7-1.0 = alto riesgo (rojo). Actúa según la urgencia.",
}


async def procesar_mensaje(mensaje: str, db: Session) -> dict:
    """
    Procesa un mensaje del técnico.
    1. Primero intenta matchear palabras clave (REGLAS_MANTENIMIENTO)
    2. Si no encuentra, delega a Ollama
    """
    mensaje_limpio = mensaje.lower().strip()
    palabras = mensaje_limpio.replace("?", "").replace("¿", "").split()

    # 1. Fast-Path: Buscar palabras clave SIEMPRE, sin importar complejidad
    for keyword, respuesta_prearmada in REGLAS_MANTENIMIENTO.items():
        if keyword in palabras:
            logger.info(f"[CHATBOT] Respuesta desde regla: {keyword}")
            return {"respuesta": respuesta_prearmada, "fuente": "reglas"}

    # 2. Slow-Path: Ollama Fallback con RAG (solo si no matchea reglas)
    try:
        respuesta_ia = await consultar_ollama(mensaje, db)
        return {"respuesta": respuesta_ia, "fuente": "ollama"}
    except Exception as e:
        logger.error(f"Error consultando a Ollama: {e}")
        # Si Ollama falla (por OOM o timeout), usamos una degradación elegante
        return {
            "respuesta": "Lo siento, mi motor de IA predictiva no está disponible en este momento para consultas complejas. Te sugiero revisar el historial de alertas y contactar al ingeniero de planta.",
            "fuente": "fallback",
        }


async def consultar_ollama(mensaje: str, db: Session) -> str:
    """Consulta a la API local de Ollama de forma asíncrona, inyectando contexto del dashboard."""
    url = f"{settings.ollama_url}/api/generate"

    # Obtener el contexto en tiempo real de la planta
    try:
        summary = get_dashboard_summary(db)
        context_str = f"- Total equipos: {summary.get('total_equipos', 0)}\n"
        context_str += f"- Alertas activas: {summary.get('alertas_activas', 0)}\n"
        context_str += f"- Equipos en riesgo (probabilidad >= 50%): {summary.get('equipos_en_riesgo', 0)}\n"

        equipos = summary.get("equipos", [])
        if equipos:
            context_str += "Detalle de equipos:\n"
            for eq in equipos:
                alertas = eq.get("alertas_activas", 0)
                prob = eq.get("ultima_probabilidad")
                prob_str = f"{prob * 100:.1f}%" if prob is not None else "N/A"
                temp = eq.get("ultima_temperatura")
                temp_str = f"{temp:.1f}°C" if temp is not None else "N/A"
                context_str += f"  * ID {eq['id']} ({eq['nombre']}): Temp {temp_str}, Riesgo Falla {prob_str}, Alertas {alertas}\n"
    except Exception as e:
        logger.error(f"Error obteniendo contexto para RAG: {e}")
        context_str = "No se pudo obtener el estado de la planta."

    # Prompt mínimo y directo (sin archivo externo)
    prompt = f"""Eres un experto en mantenimiento industrial. Responde en español, máximo 2 oraciones, sé directo.

Contexto de la planta:
{context_str}

Pregunta del técnico: {mensaje}
Respuesta:"""

    # Inyección de Few-Shot Prompting (In-Context Learning) - DESHABILITADO para mejorar velocidad
    # (Comentado porque aumenta la latencia significativamente para modelos pequeños)
    # try:
    #     historial_reciente = db.query(MensajeChat).filter(MensajeChat.fuente == "ollama").order_by(MensajeChat.id.desc()).limit(3).all()
    #     if historial_reciente:
    #         prompt += "\nEjemplos previos:\n"
    #         for msg in reversed(historial_reciente):
    #             prompt += f"P: {msg.mensaje_usuario}\nR: {msg.respuesta_ia}\n"
    # except Exception as e:
    #     logger.error(f"Error obteniendo historial: {e}")

    prompt += f"\nPregunta del técnico (Actual): {mensaje}\nRespuesta:"

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        # Aumentamos num_predict (tokens) para que no se corte y temperatura baja para precisión
        "options": {"num_predict": 250, "temperature": 0.2},
    }

    logger.debug(
        f"[CHATBOT] Enviando petición a Ollama. Longitud de prompt: {len(prompt)} caracteres"
    )

    # Timeout más corto ahora que el prompt es mínimo
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            result = data.get("response", "Sin respuesta").strip()
            logger.info(
                f"[CHATBOT] Respuesta de Ollama recibida ({len(result)} caracteres)"
            )
            return result
        except httpx.TimeoutException as e:
            logger.error(f"[CHATBOT] TIMEOUT al consultar Ollama (>60s): {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"[CHATBOT] Error HTTP de Ollama: {e.status_code} {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(
                f"[CHATBOT] Error inesperado consultando Ollama: {type(e).__name__} {e}"
            )
            raise
