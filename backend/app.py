"""
Backend FastAPI del chatbot MecánicaBot.

Endpoints:
    GET  /              -> sirve el frontend (index.html)
    GET  /health        -> verifica que Ollama y la base vectorial respondan
    POST /chat          -> recibe una pregunta y devuelve la respuesta del LLM

Levantar:
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend import llm
from backend.rag import RAGEngine


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("mecanicabot")

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"


app = FastAPI(title="MecánicaBot API", version="1.0.0")

# CORS abierto para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Carga lazy del motor RAG (al primer request o al startup)
rag_engine: RAGEngine | None = None


@app.on_event("startup")
def startup_event():
    global rag_engine
    log.info("Cargando motor RAG...")
    try:
        rag_engine = RAGEngine()
        log.info(f"RAG listo. Chunks indexados: {rag_engine.collection_size()}")
    except Exception as e:
        log.error(f"Error al cargar RAG: {e}")
        log.error("¿Ejecutaste `python scripts/ingest.py` antes?")


# ------------------- Modelos Pydantic ------------------- #

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class SourceInfo(BaseModel):
    source: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    elapsed_ms: int


class HealthResponse(BaseModel):
    ollama_ok: bool
    rag_ok: bool
    indexed_chunks: int
    model: str


# ------------------- Endpoints API ------------------- #

@app.get("/health", response_model=HealthResponse)
async def health():
    ollama_ok = await llm.health_check()
    rag_ok = rag_engine is not None
    chunks = rag_engine.collection_size() if rag_ok else 0
    return HealthResponse(
        ollama_ok=ollama_ok,
        rag_ok=rag_ok,
        indexed_chunks=chunks,
        model=llm.OLLAMA_MODEL,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if rag_engine is None:
        raise HTTPException(503, "RAG engine no inicializado. Ejecuta `python scripts/ingest.py` primero.")

    start = time.time()
    log.info(f"PREGUNTA: {req.message}")

    # 1) Retrieval
    chunks = rag_engine.retrieve(req.message)
    log.info(f"  → {len(chunks)} chunks recuperados")

    # 2) Build prompt
    messages = rag_engine.build_messages(req.message, chunks)

    # 3) Call LLM
    try:
        answer = await llm.chat(messages)
    except RuntimeError as e:
        log.error(f"Error LLM: {e}")
        raise HTTPException(502, str(e))

    elapsed_ms = int((time.time() - start) * 1000)
    log.info(f"  → respuesta generada en {elapsed_ms} ms")

    return ChatResponse(
        answer=answer,
        sources=[SourceInfo(source=c["source"], distance=c["distance"]) for c in chunks],
        elapsed_ms=elapsed_ms,
    )


# ------------------- Frontend estático ------------------- #

@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")


# Sirve CSS/JS y assets bajo /static/
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
