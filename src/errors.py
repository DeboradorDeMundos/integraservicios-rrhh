# src/errors.py
"""
Traduce excepciones técnicas a mensajes claros para el colaborador.
El detalle real se registra en consola, nunca en la interfaz.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("integrabot")


@dataclass(frozen=True)
class UserMessage:
    title: str
    body: str
    action: str
    code: str


def classify_exception(exc: BaseException) -> UserMessage:
    """Clasifica el error y oculta el traceback al usuario."""
    raw = f"{type(exc).__name__}: {exc}".lower()
    logger.exception("Error técnico de IntegraBot: %s", exc)

    if "google_api_key" in raw or "api key" in raw or "unauthenticated" in raw:
        return UserMessage(
            title="No pudimos validar el acceso al servicio",
            body=(
                "IntegraBot necesita una clave de Google AI Studio para consultar "
                "los documentos. Un administrador debe revisarla en la configuración."
            ),
            action="Si el problema continúa, avisa a Gestión de Personas o a TI.",
            code="auth",
        )

    if "429" in raw or "quota" in raw or "resource_exhausted" in raw or "rate" in raw:
        return UserMessage(
            title="El servicio está ocupado en este momento",
            body=(
                "Hay muchas consultas simultáneas o se alcanzó el límite temporal "
                "del proveedor de IA. Espera unos segundos y vuelve a intentar."
            ),
            action="No es necesario volver a escribir la pregunta: usa Reintentar.",
            code="busy",
        )

    if "not_found" in raw or "404" in raw or "is not found" in raw:
        return UserMessage(
            title="Un componente del asistente no está disponible",
            body=(
                "El modelo de consulta cambió o no está habilitado para esta cuenta. "
                "El equipo técnico debe revisar la configuración del servicio."
            ),
            action="Puedes reintentar en unos minutos. Si persiste, avisa a TI.",
            code="config",
        )

    if (
        "timeout" in raw
        or "timed out" in raw
        or "connection" in raw
        or "failed to fetch" in raw
        or "temporarily unavailable" in raw
        or "unavailable" in raw
    ):
        return UserMessage(
            title="Se interrumpió la conexión",
            body=(
                "No se pudo completar la consulta por un problema de red o del "
                "navegador. Suele resolverse recargando o reintentando."
            ),
            action="Usa Reintentar. Si entras por un enlace remoto, prueba http://localhost:8501",
            code="network",
        )

    if "generate_data" in raw or "no hay documentos" in raw or "no se pudo extraer" in raw:
        return UserMessage(
            title="Faltan los documentos oficiales",
            body=(
                "Aún no están cargados el RIOHS, el Contrato Colectivo o el "
                "Código del Trabajo. Sin ellos IntegraBot no puede responder."
            ),
            action="Un administrador debe generar o cargar los PDF en la carpeta data.",
            code="data",
        )

    if "permission" in raw or "403" in raw or "401" in raw:
        return UserMessage(
            title="No hay permiso para usar el servicio de IA",
            body=(
                "La clave está presente, pero no tiene autorización para esta "
                "operación. Corresponde a una revisión de TI."
            ),
            action="Contacta a TI indicando que IntegraBot no tiene permiso de API.",
            code="forbidden",
        )

    return UserMessage(
        title="No pudimos completar tu consulta",
        body=(
            "Ocurrió un inconveniente interno al buscar en los documentos. "
            "Tu pregunta quedó registrada y puedes volver a enviarla."
        ),
        action="Reintenta. Si se repite, deriva la consulta a Gestión de Personas.",
        code="generic",
    )


def chat_error_markdown(user_message: UserMessage) -> str:
    """Texto de burbuja de chat, sin códigos técnicos."""
    return (
        f"**{user_message.title}**\n\n"
        f"{user_message.body}\n\n"
        f"_{user_message.action}_"
    )
