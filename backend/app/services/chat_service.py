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
    "temperatura": "La alta temperatura puede deberse a fricción, sobrecarga o ventilación deficiente. Contrasta la lectura con el rubro del equipo para priorizar inspección mecánica, térmica o de proceso.",
    "vibracion": "Una vibración inusual (valores mayores a 0.5 G) puede indicar desalineación, desbalanceo o desgaste. Si supera 1.0 G, trata el equipo como riesgo alto y planifica detención controlada.",
    "vibración": "Una vibración inusual (valores mayores a 0.5 G) puede indicar desalineación, desbalanceo o desgaste. Si supera 1.0 G, trata el equipo como riesgo alto y planifica detención controlada.",
    "grafico": "Los gráficos de temperatura y vibración permiten comparar tendencias históricas por rubro (industrial, agrícola y comercial) para detectar desviaciones antes de una falla.",
    "gráfico": "Los gráficos de temperatura y vibración permiten comparar tendencias históricas por rubro (industrial, agrícola y comercial) para detectar desviaciones antes de una falla.",
    "bomba": "En bombas o sistemas de riego, revisa cavitación, filtros, presión y obstrucciones en línea antes de escalar una alerta como falla crítica.",
    "motor": "Para motores y actuadores eléctricos, revisa consumo, temperatura, ventilación y estado de rodamientos ante picos sostenidos.",
    "agricola": "En rubro agrícola prioriza continuidad operacional: revisa humedad, vibración y temperatura en riego y cosecha para evitar detenciones en ventana productiva.",
    "agrícola": "En rubro agrícola prioriza continuidad operacional: revisa humedad, vibración y temperatura en riego y cosecha para evitar detenciones en ventana productiva.",
    "comercial": "En rubro comercial prioriza seguridad y servicio: valida alarmas en cámaras de frío y escaleras mecánicas para evitar impacto a clientes.",
    "industrial": "En rubro industrial prioriza criticidad de línea: correlaciona alertas con turnos, carga y condición de proceso para reducir paradas no planificadas.",
    "rubro": "ManttoAI opera por rubros: industrial, agrícola y comercial. Usa el rubro del equipo para contextualizar umbrales y prioridad de intervención.",
    "alerta": "Si hay una alerta activa, identifica qué métrica superó el umbral y evalúa su criticidad según el rubro del equipo.",
    "mantenimiento": "Registra cada intervención en el historial del equipo. En esquema multirrubro, estandariza checklist por tipo y rubro para mejorar trazabilidad.",
    "dashboard": "El dashboard muestra el estado operativo multirrubro: equipos activos, alertas, tendencias, probabilidad de falla e historial.",
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
            "respuesta": "Lo siento, mi motor de IA predictiva no está disponible en este momento para consultas complejas. Te sugiero revisar el historial de alertas y contactar al equipo técnico.",
            "fuente": "fallback",
        }


async def consultar_ollama(mensaje: str, db: Session) -> str:
    """Consulta a la API local de Ollama de forma asíncrona, inyectando contexto del dashboard."""
    url = f"{settings.ollama_url}/api/generate"

    # Obtener el contexto en tiempo real de la operación multirrubro
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
                rubro = eq.get("rubro", "industrial")
                context_str += f"  * ID {eq['id']} ({eq['nombre']}) [{rubro}]: Temp {temp_str}, Riesgo Falla {prob_str}, Alertas {alertas}\n"

            equipos_en_riesgo = [
                eq
                for eq in equipos
                if eq.get("ultima_probabilidad") is not None
                and float(eq["ultima_probabilidad"]) >= 0.5
            ]
            if equipos_en_riesgo:
                context_str += "Equipos en riesgo por rubro:\n"
                for eq in equipos_en_riesgo:
                    rubro = eq.get("rubro", "industrial")
                    prob = float(eq["ultima_probabilidad"]) * 100
                    context_str += f"  - {eq['nombre']} (ID {eq['id']}) | Rubro: {rubro} | Riesgo: {prob:.1f}%\n"
    except Exception as e:
        logger.error(f"Error obteniendo contexto para RAG: {e}")
        context_str = "No se pudo obtener el estado operativo multirrubro."

    # Prompt mínimo y directo (sin archivo externo)
    prompt = f"""Eres un experto en mantenimiento predictivo multirrubro (Industrial, Agrícola, Comercial). Responde en español, máximo 2 oraciones, sé directo.

Contexto operativo:
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
                f"[CHATBOT] Error HTTP de Ollama: {e.response.status_code} {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(
                f"[CHATBOT] Error inesperado consultando Ollama: {type(e).__name__} {e}"
            )
            raise
