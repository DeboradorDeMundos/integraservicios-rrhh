# src/ingestion.py
"""
IE3 — Ingesta, fragmentación e indexación del corpus dual.

Separa explícitamente documentos internos (RIOHS, Contrato Colectivo)
de la normativa externa (Código del Trabajo / Ley Karin) mediante
metadata `source_type` en cada chunk vectorizado.
"""
from __future__ import annotations

import os
import shutil

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    CHUNK_SIZE,
    CORPUS,
    DATA_DIRECTORY,
    INDEX_VERSION,
    PERSIST_DIRECTORY,
    source_type_for_filename,
)


def _index_version_path() -> str:
    return os.path.join(PERSIST_DIRECTORY, ".index_version")


def _needs_rebuild() -> bool:
    """True si no hay índice o la versión de metadata cambió."""
    if not os.path.isdir(PERSIST_DIRECTORY):
        return True
    version_file = _index_version_path()
    if not os.path.isfile(version_file):
        return True
    with open(version_file, encoding="utf-8") as handle:
        return handle.read().strip() != INDEX_VERSION


def _write_index_version() -> None:
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
    with open(_index_version_path(), "w", encoding="utf-8") as handle:
        handle.write(INDEX_VERSION)


def _validate_data_directory() -> None:
    if not os.path.isdir(DATA_DIRECTORY):
        raise FileNotFoundError(
            f"No existe {DATA_DIRECTORY}. Ejecuta primero: python generate_data.py"
        )
    pdfs = [name for name in os.listdir(DATA_DIRECTORY) if name.lower().endswith(".pdf")]
    if not pdfs:
        raise FileNotFoundError(
            "No hay documentos en ./data. Ejecuta primero: python generate_data.py"
        )
    missing = set(CORPUS) - set(pdfs)
    if missing:
        raise FileNotFoundError(
            "Faltan PDF del corpus dual: "
            + ", ".join(sorted(missing))
            + ". Ejecuta: python generate_data.py"
        )


def _tag_documents(raw_documents):
    """Enriquece cada documento con source_type según el archivo de origen."""
    for doc in raw_documents:
        filename = os.path.basename(doc.metadata.get("source", ""))
        source_type = source_type_for_filename(filename)
        doc.metadata["source_type"] = source_type.value
        doc.metadata["filename"] = filename
    return raw_documents


def load_and_chunk_documents():
    """Carga PDFs, etiqueta corpus interno/externo y fragmenta."""
    _validate_data_directory()
    loader = PyPDFDirectoryLoader(DATA_DIRECTORY)
    raw_documents = loader.load()
    if not raw_documents:
        raise ValueError(
            "No se pudo extraer texto de los PDF en ./data. "
            "Verifica RIOHS_IntegraServicios_2026.pdf, "
            "Contrato_Colectivo_2026.pdf y Codigo_del_Trabajo_Chile.pdf."
        )

    tagged = _tag_documents(raw_documents)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
    )
    return splitter.split_documents(tagged)


def build_vectorstore(embeddings) -> Chroma:
    """Crea o reutiliza ChromaDB; reconstruye si cambió la versión del índice."""
    db_exists = os.path.isdir(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY)

    if db_exists and _needs_rebuild():
        print(f"Reindexando corpus (nueva version {INDEX_VERSION})...")
        try:
            shutil.rmtree(PERSIST_DIRECTORY)
        except OSError as exc:
            print(
                f"No se pudo limpiar {PERSIST_DIRECTORY} ({exc}). "
                "Cierra Streamlit si esta corriendo y vuelve a ejecutar."
            )
            raise

    if not db_exists or _needs_rebuild():
        chunks = load_and_chunk_documents()
        print("Indexando documentos PDF en ChromaDB...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
        )
        _write_index_version()
        internal = sum(1 for c in chunks if c.metadata.get("source_type") == "interno")
        external = len(chunks) - internal
        print(
            f"Se indexaron {len(chunks)} fragmentos "
            f"({internal} internos, {external} externos)."
        )
        return vectorstore

    print("Cargando base de datos ChromaDB existente...")
    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
