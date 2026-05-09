"""
Cliente HTTP para Ollama. Llama al endpoint /api/chat del servidor local
de Ollama (por defecto en http://localhost:11434).
"""

import os
from typing import AsyncIterator, List, Dict

import httpx


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
REQUEST_TIMEOUT = 120.0  # segundos


async def chat(messages: List[Dict[str, str]],
               temperature: float = 0.2,
               num_predict: int = 512) -> str:
    """
    Llama al modelo y devuelve la respuesta completa (no streaming).

    `messages` es una lista de dicts con shape:
        [{"role": "system", "content": "..."},
         {"role": "user",   "content": "..."}]
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
            "top_p": 0.9,
        },
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            r = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama devolvió error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise RuntimeError(
                f"No se pudo conectar a Ollama en {OLLAMA_HOST}. "
                f"¿Está corriendo `ollama serve`? Detalle: {e}"
            )

    data = r.json()
    return data.get("message", {}).get("content", "").strip()


async def health_check() -> bool:
    """Verifica si Ollama responde y el modelo está disponible."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            r.raise_for_status()
            tags = r.json().get("models", [])
            names = [m.get("name", "") for m in tags]
            return any(OLLAMA_MODEL in name for name in names)
        except Exception:
            return False
