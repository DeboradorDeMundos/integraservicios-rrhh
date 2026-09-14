# app.py
"""
Interfaz de chat de IntegraBot (Streamlit).

Historial en burbujas propias (sin st.chat_message) para evitar el
efecto gris de elementos 'stale' al responder la segunda consulta.
"""
import html
import logging
import os
import re

import streamlit as st
from dotenv import load_dotenv

from src.config import CORPUS_LABELS, SourceType
from src.conversation import format_chat_history
from src.errors import classify_exception
from src.rag_engine import get_rag_chain

load_dotenv()
logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(name)s] %(message)s")

st.set_page_config(
    page_title="IntegraBot | IntegraServicios S.A.",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

SUGGESTED_QUESTIONS = [
    "¿Cuál es el valor del bono de colación?",
    "¿Cuántos días administrativos pagados tengo?",
    "¿Cómo se denuncia el acoso laboral (Ley Karin)?",
    "¿Cuánto es el aguinaldo de Fiestas Patrias?",
]

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

        html, body, [class*="css"], .stApp, .stMarkdown {
            font-family: "DM Sans", "Segoe UI", sans-serif;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 7rem;
            max-width: 760px;
        }

        [data-testid="stHeader"] { background: transparent; }

        /* El gris "plomo" de Streamlit al re-renderizar */
        [data-stale="true"],
        .stElementContainer[data-stale="true"],
        .element-container.stale {
            opacity: 1 !important;
            filter: none !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071A30 0%, #0B2A4A 100%);
        }
        [data-testid="stSidebar"] * { color: #F4F8FC !important; }
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stCaption { color: #B8C9DE !important; }
        [data-testid="stSidebar"] hr { border-color: #1E4A73; }
        [data-testid="stSidebar"] button {
            background: #0B5CAB !important;
            color: #FFFFFF !important;
            border: 0 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }

        .brand-mark {
            width: 42px; height: 42px; border-radius: 12px;
            background: linear-gradient(135deg, #3B82F6, #0B5CAB);
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; color: #fff; font-size: 0.92rem;
            margin-bottom: 0.7rem;
        }

        .hero {
            background: linear-gradient(135deg, #071A30 0%, #0B5CAB 70%, #1A7AD4 100%);
            color: #FFFFFF;
            border-radius: 22px;
            padding: 1.45rem 1.5rem 1.3rem 1.5rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 16px 40px rgba(11, 42, 74, 0.22);
        }
        .hero h1 {
            color: #FFFFFF !important;
            font-size: 1.7rem;
            margin: 0 0 0.3rem 0;
            letter-spacing: -0.03em;
        }
        .hero p { color: #D7E6F7 !important; margin: 0; font-size: 0.95rem; line-height: 1.45; }
        .badge-row { margin-top: 0.95rem; display: flex; flex-wrap: wrap; gap: 0.4rem; }
        .badge {
            background: rgba(255,255,255,0.14);
            color: #FFFFFF;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 999px;
            padding: 0.25rem 0.75rem;
            font-size: 0.74rem;
        }

        .welcome {
            background: #FFFFFF;
            border: 1px solid #D7E2F0;
            border-radius: 18px;
            padding: 1.2rem 1.25rem 0.35rem 1.25rem;
            box-shadow: 0 10px 30px rgba(11, 42, 74, 0.06);
            margin-bottom: 0.7rem;
        }
        .welcome h3 { margin: 0 0 0.3rem 0; color: #0B2A4A; font-size: 1.08rem; }
        .welcome p { color: #5B6B82; margin-bottom: 0.7rem; }

        div[data-testid="stMain"] .stButton button {
            background: #FFFFFF !important;
            color: #0B2A4A !important;
            border: 1px solid #C9D8EB !important;
            border-radius: 12px !important;
            text-align: left !important;
            font-weight: 500 !important;
            min-height: 3.1rem;
            box-shadow: 0 2px 8px rgba(11, 42, 74, 0.04);
        }
        div[data-testid="stMain"] .stButton button:hover {
            border-color: #0B5CAB !important;
            color: #0B5CAB !important;
        }

        .row { display: flex; gap: 0.65rem; margin: 0.85rem 0; align-items: flex-end; }
        .row.right { justify-content: flex-end; }
        .avatar-pill {
            width: 34px; height: 34px; border-radius: 11px; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.68rem; font-weight: 700; letter-spacing: 0.02em;
        }
        .avatar-pill.bot { background: #0B2A4A; color: #fff; }
        .avatar-pill.person { background: #E8F1FB; color: #0B5CAB; }

        .bubble {
            max-width: 86%;
            padding: 0.85rem 1rem;
            border-radius: 16px;
            line-height: 1.5;
            font-size: 0.97rem;
            color: #1C2333;
        }
        .bubble.user {
            background: linear-gradient(135deg, #0B5CAB, #0A4A8C);
            color: #FFFFFF;
            border-bottom-right-radius: 5px;
            box-shadow: 0 8px 18px rgba(11, 92, 171, 0.22);
        }
        .bubble.bot {
            background: #FFFFFF;
            border: 1px solid #D7E2F0;
            border-bottom-left-radius: 5px;
            box-shadow: 0 8px 22px rgba(11, 42, 74, 0.06);
        }
        .bot-name {
            font-size: 0.72rem;
            font-weight: 700;
            color: #0B5CAB;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin: 0 0 0.45rem 0;
        }

        .thinking {
            background: #FFFFFF;
            border: 1px dashed #B9CDE6;
            border-radius: 14px;
            padding: 0.85rem 1rem;
            color: #3D5A80;
            font-size: 0.92rem;
            margin: 0.5rem 0 1rem 0;
        }
        .typing-copy { color: #1C2333; font-weight: 600; }
        .typing-sub { color: #5B6B82; font-size: 0.84rem; margin: 0.25rem 0 0.7rem 0; }
        .dots { display: flex; gap: 0.35rem; }
        .dots span {
            width: 8px; height: 8px; border-radius: 50%;
            background: #0B5CAB;
            animation: bounce 1.1s infinite ease-in-out;
        }
        .dots span:nth-child(2) { animation-delay: 0.15s; }
        .dots span:nth-child(3) { animation-delay: 0.3s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
            40% { transform: translateY(-5px); opacity: 1; }
        }

        .service-card, .chat-alert {
            background: #FFF8F1;
            border: 1px solid #F0D2B0;
            border-left: 4px solid #C05621;
            border-radius: 14px;
            padding: 1.05rem 1.1rem;
            margin: 0.35rem 0 0.7rem 0;
        }
        .kicker {
            font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase;
            color: #9A3412; font-weight: 700; margin-bottom: 0.3rem;
        }
        .chat-alert .title, .service-card h3 { color: #7C2D12; margin: 0 0 0.35rem 0; font-size: 1.02rem; }
        .chat-alert .body, .chat-alert .action, .service-card p { color: #5C4033; margin: 0 0 0.4rem 0; line-height: 1.5; }
        .chat-alert .action { margin-bottom: 0; font-size: 0.86rem; }

        [data-testid="stChatInput"] { background: #FFFFFF !important; }
        [data-testid="stChatInput"] textarea {
            color: #1C2333 !important;
            background: #FFFFFF !important;
            caret-color: #0B5CAB !important;
        }
        [data-testid="stChatInput"] textarea::placeholder { color: #66758C !important; opacity: 1 !important; }
        [data-testid="stBottomBlockContainer"] {
            background: linear-gradient(180deg, rgba(244,247,252,0), #F4F7FC 30%) !important;
        }

        .source-card {
            background: #F4F8FD;
            border: 1px solid #D7E2F0;
            border-left: 4px solid #0B5CAB;
            border-radius: 10px;
            padding: 0.7rem 0.8rem;
            margin-bottom: 0.5rem;
        }
        .source-card .meta { font-size: 0.8rem; color: #0B5CAB; font-weight: 700; margin-bottom: 0.25rem; }
        .source-card.aligned {
            border-left-color: #2F855A;
            background: #F3F9F4;
        }
        .source-card .tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-left: 0.35rem;
            color: #276749;
        }
        .source-card .corpus-tag {
            display: inline-block;
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-left: 0.35rem;
            padding: 0.1rem 0.4rem;
            border-radius: 999px;
            background: #E8F1FB;
            color: #0B5CAB;
        }
        .source-card .corpus-tag.externo {
            background: #F3ECFF;
            color: #553C9A;
        }

        .block-found, .block-derived {
            border-radius: 12px;
            padding: 0.75rem 0.85rem;
            margin: 0.45rem 0 0.65rem 0;
        }
        .block-found {
            background: #F3F9F4;
            border: 1px solid #C9E4D0;
            border-left: 4px solid #2F855A;
        }
        .block-derived {
            background: #FFF8F1;
            border: 1px solid #F0D2B0;
            border-left: 4px solid #C05621;
        }
        .block-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }
        .block-found .block-label { color: #276749; }
        .block-derived .block-label { color: #9A3412; }

        div[data-testid="stExpander"] {
            background: #F7FAFD !important;
            border: 1px solid #D7E2F0 !important;
            border-radius: 10px !important;
            margin-top: 0.35rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def cited_pdfs(answer: str) -> list[str]:
    """Nombres de PDF citados en la respuesta del modelo."""
    return [
        name.strip()
        for name in re.findall(r"Fuente:\s*([^,\]]+\.pdf)", answer or "", flags=re.I)
    ]


def render_sources(sources, answer: str = ""):
    """Trazabilidad RAG: los 4 fragmentos MMR, con la cita principal primero."""
    cited = cited_pdfs(answer)
    ranked = sorted(
        sources,
        key=lambda src: 0
        if any(name.lower() == src["name"].lower() for name in cited)
        else 1,
    )
    with st.expander("🔍 Ver fuentes documentales consultadas (RAG)", expanded=False):
        st.caption(
            "El retriever MMR siempre recupera 4 fragmentos (criterio IE3, k=4). "
            "Se muestran todos por trazabilidad. Primero van los PDF citados en la respuesta."
        )
        if not ranked:
            st.caption("No se recuperaron fragmentos para esta consulta.")
            return
        for idx, source in enumerate(ranked, 1):
            aligned = any(name.lower() == source["name"].lower() for name in cited)
            body = html.escape(source["content"]).replace("\n", "<br>")
            name = html.escape(source["name"])
            tag = '<span class="tag">Cita de la respuesta</span>' if aligned else ""
            corpus_type = source.get("source_type", SourceType.INTERNAL.value)
            corpus_label = html.escape(
                CORPUS_LABELS.get(SourceType(corpus_type), "Documento corporativo")
            )
            corpus_class = "corpus-tag externo" if corpus_type == SourceType.EXTERNAL.value else "corpus-tag"
            klass = "source-card aligned" if aligned else "source-card"
            st.markdown(
                f"""
                <div class="{klass}">
                    <div class="meta">
                        Fuente {idx} · {name} · página {source["page"]}
                        <span class="{corpus_class}">{corpus_type}</span>{tag}
                    </div>
                    <div class="body"><em>{corpus_label}</em><br>{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_alert(title: str, body: str, action: str, kicker: str = "Aviso del sistema"):
    st.markdown(
        f"""
        <div class="chat-alert">
            <div class="kicker">{html.escape(kicker)}</div>
            <div class="title">{html.escape(title)}</div>
            <div class="body">{html.escape(body)}</div>
            <div class="action">{html.escape(action)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def split_mixed_response(content: str) -> tuple[str, str]:
    """Separa lo respaldado en documentos de lo derivado a Gestión de Personas."""
    marker = "No dispongo de la información oficial"
    if marker not in content:
        return content.strip(), ""

    idx = content.find(marker)
    documented = content[:idx].strip()
    for prefix in (
        "DERIVADO A GESTIÓN DE PERSONAS:",
        "DERIVADO A GESTION DE PERSONAS:",
        "RESPUESTO CON DOCUMENTOS:",
    ):
        documented = documented.replace(prefix, "").strip()
    derived = content[idx:].strip()
    return documented, derived


def render_message(message, show_retry: bool = False, index: int = 0):
    """Pinta una burbuja propia: usuario a la derecha, IntegraBot a la izquierda."""
    if message.get("pending"):
        st.markdown(
            """
            <div class="row left">
                <div class="avatar-pill bot">IB</div>
                <div class="bubble bot" style="max-width:90%;">
                    <div class="bot-name">IntegraBot · Gestión de Personas</div>
                    <div class="typing-copy">Consultando los documentos oficiales</div>
                    <div class="typing-sub">RIOHS · Contrato Colectivo · Código del Trabajo. Esto puede tardar unos segundos.</div>
                    <div class="dots"><span></span><span></span><span></span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if message["role"] == "user":
        text = html.escape(message["content"])
        st.markdown(
            f"""
            <div class="row right">
                <div class="bubble user">{text}</div>
                <div class="avatar-pill person">TÚ</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    avatar_col, body_col = st.columns([0.11, 0.89], gap="small")
    with avatar_col:
        st.markdown('<div class="avatar-pill bot">IB</div>', unsafe_allow_html=True)
    with body_col:
        st.markdown(
            '<div class="bot-name">IntegraBot · Gestión de Personas</div>',
            unsafe_allow_html=True,
        )
        if message.get("error"):
            render_alert(
                message.get("error_title", "No pudimos completar tu consulta"),
                message.get("error_body", message.get("content", "")),
                message.get("error_action", "Puedes reintentar cuando quieras."),
            )
            if show_retry:
                st.button(
                    "Reintentar esta consulta",
                    key=f"retry_{index}",
                    on_click=retry_last_query,
                )
            return

        documented, derived = split_mixed_response(message.get("content", ""))
        if documented and derived:
            st.markdown(
                '<div class="block-found"><div class="block-label">Respondido con documentos</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(documented)
            st.markdown(
                f"""
                <div class="block-derived">
                    <div class="block-label">Derivado a Gestión de Personas</div>
                    <div>{html.escape(derived)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif derived:
            st.markdown(
                f"""
                <div class="block-derived">
                    <div class="block-label">Derivado a Gestión de Personas</div>
                    <div>{html.escape(derived)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(documented)

        if message.get("sources"):
            render_sources(message["sources"], message.get("content", ""))



def ask_question(question: str):
    st.session_state.pending_question = question


def retry_last_query():
    messages = st.session_state.messages
    if len(messages) >= 2 and messages[-1].get("error"):
        question = messages[-2].get("content", "")
        st.session_state.messages = messages[:-2]
        st.session_state.pending_question = question


def collect_sources(docs):
    return [
        {
            "name": os.path.basename(doc.metadata.get("source", "PDF")),
            "page": doc.metadata.get("page", 0) + 1,
            "content": doc.page_content,
            "source_type": doc.metadata.get("source_type", SourceType.INTERNAL.value),
        }
        for doc in docs
    ]


@st.cache_resource
def load_rag():
    """Carga una sola vez el pipeline RAG (recuperación + generación + guardrails)."""
    return get_rag_chain()


with st.sidebar:
    st.markdown('<div class="brand-mark">IS</div>', unsafe_allow_html=True)
    st.markdown("### IntegraServicios S.A.")
    st.caption("Copiloto interno de Gestión de Personas")
    st.divider()
    st.markdown("**Cómo usarlo**")
    st.markdown(
        "1. Escribe tu duda de beneficios, permisos o reglamento.\n"
        "2. IntegraBot busca en los documentos oficiales.\n"
        "3. La respuesta incluye la fuente exacta."
    )
    st.divider()
    st.markdown("**Corpus indexado (IE3)**")
    st.markdown("- **Interno:** RIOHS_IntegraServicios_2026.pdf")
    st.markdown("- **Interno:** Contrato_Colectivo_2026.pdf")
    st.markdown("- **Externo:** Codigo_del_Trabajo_Chile.pdf")
    st.divider()
    if st.button("Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.session_state.last_prompt = None
    st.caption(
        "Si el dato no está en los documentos, no se inventa: "
        "la consulta se deriva a Gestión de Personas."
    )

st.markdown(
    """
    <div class="hero">
        <h1>IntegraBot</h1>
        <p>Copiloto de RRHH y cumplimiento laboral. Respuestas con respaldo documental, no con suposiciones.</p>
        <div class="badge-row">
            <span class="badge">RIOHS IntegraServicios 2026</span>
            <span class="badge">Contrato Colectivo</span>
            <span class="badge">Código del Trabajo / Ley Karin</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    pipeline = load_rag()
except Exception as exc:
    info = classify_exception(exc)
    st.markdown(
        f"""
        <div class="service-card">
            <div class="kicker">Servicio temporalmente no disponible</div>
            <h3>{html.escape(info.title)}</h3>
            <p>{html.escape(info.body)}</p>
            <p>{html.escape(info.action)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Reintentar conexión", use_container_width=True):
        load_rag.clear()
        st.rerun()
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None

show_welcome = (
    not st.session_state.messages and not st.session_state.pending_question
)

if show_welcome:
    st.markdown(
        """
        <div class="welcome">
            <h3>¿En qué te ayudo hoy?</h3>
            <p>Elige una pregunta frecuente o escribe la tuya en el recuadro de abajo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for idx, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[idx % 2]:
            st.button(
                question,
                key=f"suggest_{idx}",
                use_container_width=True,
                on_click=ask_question,
                args=(question,),
            )

for index, message in enumerate(st.session_state.messages):
    is_last = index == len(st.session_state.messages) - 1
    render_message(message, show_retry=bool(message.get("error") and is_last), index=index)

typed_input = st.chat_input("Escribe tu consulta: beneficios, permisos, reglamento...")
user_input = typed_input or st.session_state.pop("pending_question", None)
busy = bool(
    st.session_state.messages and st.session_state.messages[-1].get("pending")
)

if user_input and not busy and st.session_state.last_prompt != user_input:
    st.session_state.last_prompt = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append(
        {"role": "assistant", "pending": True, "content": "", "sources": []}
    )
    st.rerun()

if busy:
    query = next(
        msg["content"]
        for msg in reversed(st.session_state.messages)
        if msg["role"] == "user"
    )
    try:
        history = format_chat_history(st.session_state.messages[:-2])
        response, retrieved_docs = pipeline.query(query, chat_history=history)
        sources = collect_sources(retrieved_docs)
        st.session_state.messages[-1] = {
            "role": "assistant",
            "content": response,
            "sources": sources,
            "error": False,
        }
    except Exception as exc:
        info = classify_exception(exc)
        st.session_state.messages[-1] = {
            "role": "assistant",
            "content": info.body,
            "sources": [],
            "error": True,
            "error_title": info.title,
            "error_body": info.body,
            "error_action": info.action,
        }
    st.rerun()
