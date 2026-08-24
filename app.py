# app.py
"""
Interfaz de chat de IntegraBot (Streamlit).

Muestra historial de conversacion, respuestas del RAG y los fragmentos
de origen recuperados desde ChromaDB para cada consulta.
"""
import os

import streamlit as st
from dotenv import load_dotenv

from src.rag_engine import get_rag_chain

load_dotenv()

st.set_page_config(
    page_title="IntegraBot - Copiloto RRHH",
    page_icon="🤖",
    layout="wide",
)

# Tema corporativo azul / oscuro
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #0b1f3a 0%, #102a4c 45%, #0e223d 100%);
            color: #e8eef7;
        }
        h1, h2, h3, p, label, .stMarkdown, .stCaption {
            color: #e8eef7 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #0a1a30;
            border-right: 1px solid #1f4e8a;
        }
        [data-testid="stChatMessage"] {
            background-color: rgba(16, 42, 76, 0.75);
            border: 1px solid #1f4e8a;
            border-radius: 12px;
        }
        .stChatInput textarea, .stChatInput input {
            color: #0b1f3a;
        }
        div[data-testid="stExpander"] {
            background-color: #102a4c;
            border: 1px solid #2b6cb0;
            border-radius: 8px;
        }
        .block-container {
            padding-top: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("IntegraBot: Copiloto de RRHH y Cumplimiento Laboral")
st.caption(
    "IntegraServicios S.A. | Respuestas respaldadas en RIOHS, "
    "Contrato Colectivo y Codigo del Trabajo"
)

with st.sidebar:
    st.header("IntegraServicios S.A.")
    st.markdown(
        "Asistente interno para consultas de **beneficios**, **reglamento** "
        "y **normativa laboral**."
    )
    st.divider()
    st.markdown("**Fuentes indexadas**")
    st.markdown("- RIOHS 2026")
    st.markdown("- Contrato Colectivo 2026")
    st.markdown("- Codigo del Trabajo")
    st.divider()
    st.caption(
        "Si la respuesta no esta en los documentos oficiales, IntegraBot "
        "deriva la consulta a Gestion de Personas y no inventa montos ni plazos."
    )


@st.cache_resource
def load_rag():
    """Carga una sola vez la cadena RAG y el retriever."""
    return get_rag_chain()


try:
    rag_chain, retriever = load_rag()
except Exception as exc:
    st.error(f"Error al inicializar el sistema RAG: {exc}")
    st.info(
        "Asegurate de haber configurado tu OPENAI_API_KEY en el archivo .env "
        "y de haber ejecutado `python generate_data.py`."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("Ver fuentes documentales consultadas (RAG)"):
                for idx, source in enumerate(message["sources"], 1):
                    st.write(
                        f"**Fuente [{idx}]:** `{source['name']}` (Pagina {source['page']})"
                    )
                    st.caption(source["content"])
                    st.divider()

if user_input := st.chat_input(
    "Escribe tu consulta sobre beneficios, permisos o reglamento..."
):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Consultando reglamentos internos y normativa laboral..."):
            retrieved_docs = retriever.invoke(user_input)
            response = rag_chain.invoke(user_input)

            sources = []
            for doc in retrieved_docs:
                sources.append(
                    {
                        "name": os.path.basename(doc.metadata.get("source", "PDF")),
                        "page": doc.metadata.get("page", 0) + 1,
                        "content": doc.page_content,
                    }
                )

            st.markdown(response)
            with st.expander("Ver fuentes documentales consultadas (RAG)"):
                for idx, source in enumerate(sources, 1):
                    st.write(
                        f"**Fuente [{idx}]:** `{source['name']}` (Pagina {source['page']})"
                    )
                    st.caption(source["content"])
                    st.divider()

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "sources": sources}
    )
