# IntegraBot — Asistente RAG de RRHH y Cumplimiento Laboral

Sistema de **Retrieval-Augmented Generation (RAG)** para IntegraServicios S.A. El asistente **IntegraBot** responde consultas de colaboradores sobre el Reglamento Interno (RIOHS), el Contrato Colectivo y extractos del Código del Trabajo, citando la fuente y evitando alucinaciones.

## Arquitectura

```
Consulta del trabajador
        │
        ▼
  Streamlit (app.py)
        │
        ▼
  Motor RAG (src/rag_engine.py)
        │
        ├── Carga PDFs (PyPDFDirectoryLoader)
        ├── Chunking (RecursiveCharacterTextSplitter, 500 / 50)
        ├── Embeddings OpenAI (text-embedding-3-small)
        ├── ChromaDB local (./chroma_db)
        └── LLM gpt-4o-mini + System Prompt (src/prompts.py)
        │
        ▼
  Respuesta con citas + fragmentos de origen
```

Flujo resumido:

1. Los documentos de `data/` se fragmentan e indexan una sola vez en ChromaDB.
2. Cada pregunta recupera los 4 fragmentos más relevantes (búsqueda MMR).
3. El modelo responde **solo** con ese contexto. Si no hay evidencia, deriva la consulta a Gestión de Personas.

## Requisitos

- Python 3.10 o superior
- Cuenta de OpenAI y una API Key con acceso a embeddings y chat

## Instalación

```bash
git clone https://github.com/DeboradorDeMundos/integraservicios-rrhh.git
cd integraservicios-rrhh
```

Crea y activa un entorno virtual:

```bash
python -m venv venv

# Windows (si python no se reconoce, usa: py -m venv venv)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configuración de la API Key

Copia la plantilla y edita el archivo `.env`:

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Abre `.env` y reemplaza el valor:

```
OPENAI_API_KEY=sk-proj-tu-api-key-aqui
```

No subas el archivo `.env` a GitHub. Ya está incluido en `.gitignore`.

## Generar documentos de prueba

El repositorio incluye un generador de PDFs simulados (RIOHS, Contrato Colectivo y Código del Trabajo):

```bash
python generate_data.py
```

Los archivos quedan en `data/`:

- `RIOHS_2026.pdf`
- `Contrato_Colectivo_2026.pdf`
- `Codigo_del_Trabajo.pdf`

## Ejecutar la aplicación

```bash
streamlit run app.py
```

El navegador se abrirá con el chat de IntegraBot. La primera consulta indexa los PDFs en `./chroma_db` (puede tardar unos segundos). Las siguientes reutilizan el índice local.

## Preguntas de prueba sugeridas

- ¿Cuál es el valor del bono de colación?
- ¿Cuántos días de permiso administrativo tengo?
- ¿Qué dice el reglamento sobre la Ley Karin?
- ¿Cuánto es el aguinaldo de Fiestas Patrias?
- ¿Cuál es la jornada ordinaria de la empresa?

## Estructura del proyecto

```
integraservicios-rrhh/
├── data/                  # PDFs corporativos / legales
├── src/
│   ├── __init__.py
│   ├── prompts.py         # System Prompt y guardrails
│   └── rag_engine.py      # Carga, chunking, ChromaDB y cadena RAG
├── generate_data.py       # Genera PDFs de prueba
├── app.py                 # Interfaz Streamlit
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Notas de evaluación

- Las respuestas deben citar la fuente exacta, por ejemplo `[RIOHS 2026, Art. 14]` o `[Contrato Colectivo, Cláusula 5]`.
- Si el dato no está en los documentos, IntegraBot **no inventa** montos, plazos ni artículos.
- La base vectorial (`chroma_db/`) y las claves (`.env`) no se versionan.

## Licencia de uso académico

Proyecto de evaluación académica. Los PDFs generados son **simulados** con fines de demostración y no sustituyen el texto oficial del Código del Trabajo ni los instrumentos colectivos reales de una empresa.
