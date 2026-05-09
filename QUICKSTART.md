# QUICKSTART — Levantar el chatbot en 10 minutos

Esta guía es para quien va a hostear el sistema. Probado en GTX 1060 6GB,
i7-4790, 16 GB RAM.

## Paso 1: instalar Ollama y descargar el modelo (~10 min, 5 GB de descarga)

### Windows
1. Descargar instalador desde <https://ollama.com/download/windows>
2. Ejecutar el .exe. Ollama queda corriendo automáticamente como servicio en background.

### Linux / WSL
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Verificar instalación
Abrir una terminal y ejecutar:
```bash
ollama --version
```

### Descargar el modelo
```bash
ollama pull llama3.1:8b
```
(Este comando descarga ~4.7 GB. Tomar agüita.)

### Probar el modelo
```bash
ollama run llama3.1:8b "Hola, di una sola palabra"
```
Si responde, el LLM ya está operativo. Salir con `/bye`.

---

## Paso 2: clonar el repo y crear entorno Python (~3 min)

```bash
git clone <URL-del-repo>
cd <carpeta-del-proyecto>

# Crear entorno virtual
python -m venv venv

# Activarlo:
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Paso 3: ingestar el corpus (~2 min)

Con el entorno virtual activado:

```bash
python scripts/ingest.py
```

Salida esperada:
```
=== Ingestión del corpus ===
[1/4] Leyendo corpus...
  [+] 01_aceite_motor.txt (...)
  [+] 02_neumaticos.txt (...)
  ...
[4/4] Indexando en ChromaDB...
  → Indexados N/N
✅ Listo. Total en colección: N chunks
```

La primera ejecución descarga el modelo de embeddings (~118 MB).

---

## Paso 4: levantar el backend

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Salida esperada:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
mecanicabot | Cargando motor RAG...
mecanicabot | RAG listo. Chunks indexados: N
```

---

## Paso 5: abrir el navegador

Ir a <http://localhost:8000>

Verificar que en el panel superior los dos indicadores (LLM y RAG) estén verdes.

Probar con una de las preguntas de validación de `docs/preguntas_validacion.md`.

---

## Solución de problemas frecuentes

### `RuntimeError: No se pudo conectar a Ollama`
Ollama no está corriendo. En Linux:
```bash
ollama serve
```
En Windows debería iniciar solo. Si no, lanzar `ollama list` para forzar arranque.

### `RAG engine no inicializado`
Faltó correr `python scripts/ingest.py`.

### Respuestas muy lentas (>30 seg por pregunta)
Verificar que Ollama esté usando la GPU:
```bash
ollama ps
```
Debe mostrar el modelo con `100% GPU` o cerca. Si muestra `100% CPU`, los drivers
NVIDIA o CUDA no están bien instalados. En GTX 1060 con drivers actualizados se
espera ~15–20 tokens/s.

### El modelo responde en inglés
Esto solo pasa si la pregunta usa términos muy ambiguos. El prompt del sistema
está fijado en español; es raro pero posible. Reintentar formulando la pregunta
con vocabulario más explícito.

### Quiero agregar más documentos al corpus
Copiar PDF o TXT a `corpus/` y reindexar:
```bash
python scripts/ingest.py --reset
```

---

## Comandos útiles para grabar el video

Antes de grabar, asegurarse de:
- Cerrar pestañas innecesarias del navegador.
- Maximizar la ventana del navegador en una resolución 1920×1080.
- Tener un cronómetro o las preguntas listas para pegar.
- Verificar que los indicadores LLM y RAG estén verdes.

Recomendamos OBS Studio para grabar pantalla + voz simultáneamente.
