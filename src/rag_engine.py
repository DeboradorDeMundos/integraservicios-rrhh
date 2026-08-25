# src/rag_engine.py
"""
Pipeline RAG dual de IntegraBot (criterios IE3 e IE4).

Responsabilidades:
- Cargar PDFs internos (RIOHS, Contrato Colectivo) y externos
  (Código del Trabajo / Ley Karin) desde ./data
- Fragmentar (~500 caracteres, overlap 50)
- Indexar vectores en ChromaDB local
- Exponer la cadena LCEL y el retriever MMR para la UI
"""
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.prompts import SYSTEM_PROMPT

load_dotenv()

PERSIST_DIRECTORY = "./chroma_db"
DATA_DIRECTORY = "./data"

# Modelo vigente de embeddings en Google AI Studio.
# La referencia "models/embedding-001" fue retirada (error 404); se usa el sucesor oficial.
EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"


def format_docs(docs):
    """
    Concatena fragmentos recuperados e inyecta trazabilidad
    (nombre de archivo y página) para el LLM y la UI.
    """
    formatted = []
    for doc in docs:
        source_name = os.path.basename(doc.metadata.get("source", "Documento"))
        page = doc.metadata.get("page", 0) + 1
        formatted.append(
            f"--- Fuente: {source_name} (Pág. {page}) ---\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


def _build_vectorstore(embeddings):
    """Crea o reutiliza el índice vectorial local de ChromaDB."""
    db_exists = os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY)

    if not db_exists:
        if not os.path.isdir(DATA_DIRECTORY) or not any(
            name.lower().endswith(".pdf") for name in os.listdir(DATA_DIRECTORY)
        ):
            raise FileNotFoundError(
                "No hay documentos en ./data. Ejecuta primero: python generate_data.py"
            )

        print("Indexando documentos PDF en ChromaDB con Google Embeddings...")
        loader = PyPDFDirectoryLoader(DATA_DIRECTORY)
        raw_documents = loader.load()

        if not raw_documents:
            raise ValueError(
                "No se pudo extraer texto de los PDF en ./data. "
                "Verifica RIOHS_IntegraServicios_2026.pdf, "
                "Contrato_Colectivo_2026.pdf y Codigo_del_Trabajo_Chile.pdf."
            )

        # Chunking ~500 con overlap 50 y separadores jurídicos.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "Artículo", "Cláusula", " ", ""],
        )
        chunks = text_splitter.split_documents(raw_documents)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
        )
        print(f"Se indexaron {len(chunks)} fragmentos exitosamente.")
        return vectorstore

    print("Cargando base de datos ChromaDB existente...")
    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )


def initialize_rag_system():
    """
    Inicializa ChromaDB y la cadena RAG con Google Gemini 2.5 Flash.

    Returns:
        tuple: (rag_chain, retriever) para generar respuestas y mostrar fuentes.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "Falta GOOGLE_API_KEY. Copia .env.example a .env y coloca tu clave de Google AI Studio."
        )

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = _build_vectorstore(embeddings)

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "lambda_mult": 0.75},
    )

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.1)

    # Cadena LCEL: retriever -> prompt (contexto + pregunta) -> Gemini -> texto.
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | SYSTEM_PROMPT
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


def get_rag_chain():
    """Punto de entrada usado por la interfaz Streamlit."""
    return initialize_rag_system()
