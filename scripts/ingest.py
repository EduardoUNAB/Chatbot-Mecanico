"""
Script de ingestión del corpus.

Lee todos los archivos PDF y TXT de la carpeta `corpus/`, los divide en chunks
con solapamiento, calcula embeddings con sentence-transformers y los indexa
en ChromaDB persistente en `chroma_db/`.

Uso:
    python scripts/ingest.py

Para reindexar desde cero:
    python scripts/ingest.py --reset
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List

import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# Configuración
ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "corpus"
DB_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "mecanica_automotriz"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 900        # caracteres aproximados por chunk
CHUNK_OVERLAP = 200     # solapamiento entre chunks consecutivos
BATCH_SIZE = 64         # tamaño de batch para indexación


def read_pdf(path: Path) -> str:
    """Extrae todo el texto de un PDF."""
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception as e:
            print(f"  [!] Error en página de {path.name}: {e}", file=sys.stderr)
            text = ""
        pages.append(text)
    return "\n".join(pages)


def read_txt(path: Path) -> str:
    """Lee un archivo de texto plano."""
    return path.read_text(encoding="utf-8", errors="ignore")


def clean_text(text: str) -> str:
    """Limpieza básica: normaliza saltos de línea y espacios múltiples."""
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Divide el texto en chunks con solapamiento. Intenta cortar en finales de
    oración para no partir frases por la mitad.
    """
    if len(text) <= size:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        # Si no estamos al final, buscar el último punto/salto cerca del corte
        if end < len(text):
            # Buscar un buen punto de corte hacia atrás
            for sep in (". ", ".\n", "\n\n", "\n", " "):
                idx = text.rfind(sep, start + size // 2, end)
                if idx != -1:
                    end = idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end - overlap > start else end
    return chunks


def load_corpus(corpus_dir: Path) -> List[dict]:
    """
    Recorre el corpus y devuelve una lista de documentos:
    [{"source": "manual.pdf", "text": "..."}]
    """
    docs = []
    if not corpus_dir.exists():
        print(f"[!] No existe la carpeta de corpus: {corpus_dir}", file=sys.stderr)
        return docs

    for path in sorted(corpus_dir.iterdir()):
        if path.is_dir():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                text = read_pdf(path)
            elif suffix in (".txt", ".md"):
                text = read_txt(path)
            else:
                print(f"  [-] Saltando {path.name} (extensión no soportada)")
                continue
        except Exception as e:
            print(f"  [!] Error leyendo {path.name}: {e}", file=sys.stderr)
            continue

        text = clean_text(text)
        if not text:
            print(f"  [-] {path.name} vacío tras limpieza, saltado")
            continue

        docs.append({"source": path.name, "text": text})
        print(f"  [+] {path.name} ({len(text):,} caracteres)")
    return docs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true",
                        help="Borra la colección existente antes de indexar")
    args = parser.parse_args()

    print(f"\n=== Ingestión del corpus ===")
    print(f"Carpeta corpus: {CORPUS_DIR}")
    print(f"Base vectorial: {DB_DIR}")
    print(f"Modelo embeddings: {EMBEDDING_MODEL}\n")

    print("[1/4] Leyendo corpus...")
    docs = load_corpus(CORPUS_DIR)
    if not docs:
        print("\n[!] No se encontraron documentos en corpus/. Aborta.")
        sys.exit(1)
    print(f"  → {len(docs)} documentos cargados\n")

    print("[2/4] Generando chunks...")
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{doc['source']}::{i}",
                "text": chunk,
                "metadata": {"source": doc["source"], "chunk_index": i},
            })
        print(f"  [+] {doc['source']}: {len(chunks)} chunks")
    print(f"  → {len(all_chunks)} chunks totales\n")

    print("[3/4] Cargando modelo de embeddings...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"  → Modelo listo (dim={model.get_sentence_embedding_dimension()})\n")

    print("[4/4] Indexando en ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(DB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    if args.reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"  [!] Colección '{COLLECTION_NAME}' eliminada")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Indexar por batches
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        collection.add(
            ids=[c["id"] for c in batch],
            documents=texts,
            embeddings=embeddings,
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"  → Indexados {min(i + BATCH_SIZE, len(all_chunks))}/{len(all_chunks)}")

    print(f"\n✅ Listo. Total en colección: {collection.count()} chunks")
    print(f"   Base persistida en: {DB_DIR}\n")


if __name__ == "__main__":
    main()
