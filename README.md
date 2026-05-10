# MecánicaBot — Asistente Conversacional de Mecánica Automotriz Básica

> Proyecto 1 — Fase 2 — CINF104 Aprendizaje de Máquinas — UNAB 2026
> Universidad Andrés Bello — Facultad de Ingeniería

Chatbot que responde preguntas sobre **mecánica automotriz básica y mantenimiento preventivo de vehículos**, usando un LLM local (Llama 3.1 8B vía Ollama) con una arquitectura **RAG (Retrieval-Augmented Generation)** sobre un corpus de manuales de usuario, guías técnicas y normas de mantenimiento.

## Autores

- Eduardo Zepeda
- Iosef Cornejo
- Vicente Díaz
- Fernando Rojas
- Fernando Chavez

## Arquitectura

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Frontend   │ ────► │   Backend    │ ────► │    Ollama    │
│  HTML + JS   │       │   FastAPI    │       │  Llama 3.1   │
└──────────────┘       └──────┬───────┘       └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   ChromaDB   │
                       │  (vectores)  │
                       └──────────────┘
```

1. El usuario hace una pregunta desde la interfaz web.
2. El backend convierte la pregunta en embedding y consulta ChromaDB.
3. ChromaDB devuelve los `k` chunks más relevantes del corpus.
4. El backend construye un prompt que incluye los chunks como contexto.
5. Ollama (Llama 3.1 8B) genera la respuesta basada únicamente en ese contexto.
6. La respuesta se devuelve al frontend.

## Requisitos

- **Hardware**: GPU con ≥6 GB VRAM recomendado (probado en GTX 1060 6GB).
- **Software**:
  - Python Entre 3.10 y 3.12 (No usar python 3.13)
  - [Ollama](https://ollama.com/) instalado y corriendo
  - 16 GB RAM mínimo

## Instalación

### 1. Instalar Ollama y descargar el modelo

```bash
# Linux / WSL:
curl -fsSL https://ollama.com/install.sh | sh

# Windows / Mac: descargar instalador desde https://ollama.com/download
```

Descargar Llama 3.1 8B cuantizado:

```bash
ollama pull llama3.1:8b
```

Verificar que el servicio esté corriendo:

```bash
ollama list
# Debe aparecer "llama3.1:8b" en la lista
```

### 2. Clonar el repositorio e instalar dependencias

```bash
git clone <URL-DEL-REPO>
cd <nombre-carpeta>
python -m venv venv
source venv/bin/activate     # en Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Preparar el corpus

Colocar los archivos PDF/TXT del dominio dentro de la carpeta `corpus/`. Ya se incluyen ejemplos. Después, ejecutar el script de ingestión:

```bash
python scripts/ingest.py
```

Esto crea la base vectorial en `chroma_db/`.

### 4. Levantar el backend

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Abrir el frontend

Abrir el navegador en: <http://localhost:8000>

## Estructura del repositorio

```
.
├── README.md
├── requirements.txt
├── backend/
│   ├── app.py              # FastAPI: endpoints /chat y archivos estáticos
│   ├── rag.py              # Lógica de retrieval + construcción de prompt
│   └── llm.py              # Cliente Ollama
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── chat.js
├── corpus/                 # PDFs y TXT del dominio
├── scripts/
│   └── ingest.py           # Chunking + embeddings + ChromaDB
├── chroma_db/              # (generado) base vectorial
└── docs/
    ├── Demo_Video.mp4
    ├── Informe_ChatbotMecanico.pdf
    └── preguntas_validacion.md

```

## Pruebas

Las 10 preguntas oficiales de validación están en `docs/preguntas_validacion.md`. El informe completo de pruebas (con análisis de respuestas, limitaciones y mejoras) está en `docs/Informe_ChatbotMecanico.pdf`.

## Licencia

Proyecto académico — UNAB 2026.
