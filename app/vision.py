"""Cohere Vision: una foto -> estado exterior + justificación breve."""
import base64
import json
import os
import re
import cohere
from .config import ESTADOS

MODELO_VISION = "command-a-vision-07-2025"
# Tarea C1-A: Prompt para clasificación visual del estado exterior del vehículo.
PROMPT = """Eres un perito tasador experto en automoción. Tu única tarea es evaluar el estado visual EXTERIOR del vehículo que aparece en la fotografía y seleccionar exactamente una categoría.

Debes elegir obligatoriamente una de estas cuatro categorías según los criterios visibles:
- "like new": estado impecable como nuevo, pintura impoluta sin arañazos ni golpes, ópticas y lunas perfectas.
- "excellent": excelente estado general, desgaste mínimo prácticamente imperceptible propio de uso muy cuidadoso.
- "good": buen estado habitual, presenta marcas leves de uso, pequeños arañazos o roces superficiales en pintura o paragolpes sin abolladuras graves.
- "fair": estado aceptable con desperfectos evidentes, desgaste notable, arañazos visibles continuos, abolladuras, desalineaciones o paneles deteriorados.

Reglas obligatorias:
1. Evalúa únicamente la carrocería y los elementos exteriores visibles en la imagen.
2. Está estrictamente prohibido realizar afirmaciones, conjeturas o deducciones sobre el motor, mecánica, funcionamiento interno, historial de accidentes o kilometraje.
3. Si en la imagen no se aprecia claramente un automóvil exterior completo o suficiente para una valoración razonable (por ejemplo, imagen borrosa, interior exclusivo, recorte de una pieza suelta, rueda aislada o imagen no automovilística), debes responder con la categoría "unknown". No adivines.
4. Responde ÚNICAMENTE con un objeto JSON válido, sin bloques de código markdown, sin explicaciones adicionales fuera del JSON ni texto introductorio.

Formato exacto de respuesta JSON:
{"condition": "<like new|excellent|good|fair|unknown>", "reason": "<explicación breve y concisa en español basada únicamente en los detalles visuales exteriores observados>"}"""



class VisionError(Exception):
    """Error de proveedor o de respuesta no interpretable."""


def parsear_respuesta(texto: str) -> tuple[str, str]:
    """Helper ya implementado: valida el JSON que responde la IA."""
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.I)
    if not limpio.startswith("{"):
        a, b = limpio.find("{"), limpio.rfind("}")
        if a >= 0 and b > a:
            limpio = limpio[a:b+1]
    try:
        obj = json.loads(limpio)
    except (ValueError, TypeError) as exc:
        raise VisionError("Cohere no devolvió un JSON interpretable.") from exc
    estado = str(obj.get("condition", "")).strip().lower()
    razon = str(obj.get("reason", "")).strip()[:350]
    if estado not in (*ESTADOS, "unknown"):
        raise VisionError(f"Cohere devolvió una categoría inesperada: {estado!r}")
    return estado, razon or "Sin justificación visible."


def clasificar_estado(contenido: bytes, mimetype: str) -> tuple[str, str, str]:
    """TODO C1: devuelve (condition, reason, fuente)."""
    if os.getenv("VISION_MOCK", "0") == "1":
        return "good", "Modo demostración: estado fijo, sin analizar la fotografía.", "MOCK"
    token = os.getenv("COHERE_API_KEY", "").strip()
    if not token:
        raise VisionError("Falta COHERE_API_KEY en el archivo .env")
    if not PROMPT.strip():
        raise VisionError("Falta redactar el prompt visual: tarea C1-A.")

    data_url = f"data:{mimetype};base64,{base64.b64encode(contenido).decode('utf-8')}"
    try:
        cliente = cohere.ClientV2(api_key=token)
        respuesta = cliente.chat(
            model=MODELO_VISION,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        )
        if not respuesta.message or not respuesta.message.content:
            raise VisionError("Cohere devolvió una respuesta vacía.")
        bloque = respuesta.message.content[0]
        texto = getattr(bloque, "text", None)
        if not texto:
            raise VisionError("Cohere devolvió un bloque de contenido sin texto.")
        estado, razon = parsear_respuesta(texto)
        return estado, razon, "COHERE"

    except VisionError:
        raise
    except Exception as exc:
        raise VisionError(f"Error al comunicar con la API de Cohere Vision: {exc}") from exc

