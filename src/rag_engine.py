# src/rag_engine.py
"""
Motor RAG de IntegraBot.

Carga PDFs corporativos, fragmenta el texto, indexa vectores en ChromaDB
y expone la cadena de consulta (retriever + LLM) con citas de fuente.
"""
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.prompts import SYSTEM_PROMPT

load_dotenv()

PERSIST_DIRECTORY = "./chroma_db"
DATA_DIRECTORY = "./data"


def format_docs(docs):
    """Concatena el contenido de los fragmentos recuperados con su fuente."""
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
        if not os.path.isdir(DATA_DIRECTORY) or not os.listdir(DATA_DIRECTORY):
            raise FileNotFoundError(
                "No hay documentos en ./data. Ejecuta primero: python generate_data.py"
            )

        print("Indexando documentos PDF en ChromaDB...")
        loader = PyPDFDirectoryLoader(DATA_DIRECTORY)
        raw_documents = loader.load()

        if not raw_documents:
            raise ValueError(
                "No se pudo extraer texto de los PDF en ./data. "
                "Verifica que existan RIOHS_2026.pdf, Contrato_Colectivo_2026.pdf "
                "y Codigo_del_Trabajo.pdf."
            )

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
    Inicializa ChromaDB y la cadena RAG.

    Returns:
        tuple: (rag_chain, retriever) para generar respuestas y mostrar fuentes.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "Falta OPENAI_API_KEY. Copia .env.example a .env y coloca tu clave."
        )

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = _build_vectorstore(embeddings)

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "lambda_mult": 0.75},
    )

    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


def get_rag_chain():
    """
    Configura la cadena de consulta RAG.

    Devuelve la cadena (respuesta generada) y el retriever (fuentes citadas).
    """
    return initialize_rag_system()
