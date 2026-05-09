"""
Módulo RAG: realiza la búsqueda de chunks relevantes en ChromaDB
y construye el prompt final para el LLM.
"""

from pathlib import Path
from typing import List, Dict, Tuple

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# Configuración
ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "mecanica_automotriz"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 6                          # cuántos chunks recuperar
MAX_DISTANCE = 1.5                 # filtra chunks demasiado lejanos (cosine distance)


SYSTEM_PROMPT = """Eres MecánicaBot, un asistente experto en mecánica automotriz básica y mantenimiento preventivo de vehículos. Tu propósito es ayudar a usuarios comunes con dudas sobre el cuidado y funcionamiento de sus autos, entregando respuestas técnicamente correctas y completas.

REGLAS DE CONTENIDO:
1. Responde ÚNICAMENTE usando la información del CONTEXTO que se te entrega. No uses conocimiento general de tu entrenamiento si no aparece en el contexto.
2. Si la pregunta NO se puede responder con el contexto provisto, di exactamente: "No tengo información suficiente en mi base de conocimiento para responder esa pregunta con precisión." y sugiere consultar a un mecánico calificado.
3. Si la pregunta no es sobre mecánica automotriz o mantenimiento de vehículos, responde: "Soy un asistente especializado en mecánica automotriz. Solo puedo ayudarte con dudas sobre el cuidado y funcionamiento de tu vehículo."
4. Nunca inventes datos, marcas, modelos ni cifras que no aparezcan en el contexto.

REGLAS DE COMPLETITUD (MUY IMPORTANTE):
5. Si el contexto contiene una LISTA de elementos (síntomas, causas, pasos, funciones, tipos), debes mencionar TODOS los elementos relevantes de la lista, no solo algunos. No resumas listas a 2 o 3 ítems si el contexto tiene más.
6. Si el contexto contiene ADVERTENCIAS de seguridad (riesgos de quemaduras, daños mecánicos, peligro de accidente), DEBES incluirlas en tu respuesta. Son información crítica.
7. Si el contexto contiene VALORES NUMÉRICOS (rangos de kilómetros, presiones, voltajes, temperaturas), inclúyelos textualmente en la respuesta. No los omitas ni los redondees arbitrariamente.
8. Si la pregunta es sobre un procedimiento, presenta TODOS los pasos del procedimiento que aparecen en el contexto, en orden.

REGLAS DE FORMATO:
9. Usa lenguaje claro y accesible, pero sin omitir tecnicismos relevantes que aparezcan en el contexto.
10. Cuando la respuesta tenga múltiples puntos, organízalos en una lista numerada o con guiones para facilitar la lectura.
11. Cierra con una recomendación concreta de acción cuando el contexto la sugiera (por ejemplo: "consultar a un mecánico", "no continuar conduciendo", "verificar mensualmente").
12. Responde siempre en español."""


class RAGEngine:
    """Encapsula la lógica de retrieval. Se instancia una vez al levantar la app."""

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=str(DB_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_collection(COLLECTION_NAME)
        self._encoder = SentenceTransformer(EMBEDDING_MODEL)

    def retrieve(self, query: str, k: int = TOP_K) -> List[Dict]:
        """
        Devuelve los chunks más relevantes para la consulta.
        Cada elemento: {"text": str, "source": str, "distance": float}
        """
        embedding = self._encoder.encode([query]).tolist()
        results = self._collection.query(
            query_embeddings=embedding,
            n_results=k,
        )

        chunks = []
        if not results["documents"]:
            return chunks

        for text, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if distance > MAX_DISTANCE:
                continue
            chunks.append({
                "text": text,
                "source": metadata.get("source", "desconocido"),
                "distance": float(distance),
            })
        return chunks

    def build_messages(self, query: str, chunks: List[Dict]) -> List[Dict[str, str]]:
        """Construye la lista de mensajes lista para enviar a Ollama."""
        if not chunks:
            context_block = "(No se encontraron documentos relevantes en la base de conocimiento.)"
        else:
            parts = []
            for i, c in enumerate(chunks, 1):
                parts.append(f"[Fragmento {i} — fuente: {c['source']}]\n{c['text']}")
            context_block = "\n\n".join(parts)

        user_content = (
            f"CONTEXTO:\n{context_block}\n\n"
            f"PREGUNTA DEL USUARIO:\n{query}\n\n"
            f"Responde siguiendo estrictamente las reglas del sistema."
        )

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def collection_size(self) -> int:
        return self._collection.count()
