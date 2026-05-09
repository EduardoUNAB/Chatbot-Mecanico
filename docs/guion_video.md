# Guion del Video de Demostración — Fase 2

**Duración objetivo: 5–7 minutos**
**Herramienta sugerida: OBS Studio (gratis) o Loom**
**Resolución: 1920×1080 mínimo**

---

## Estructura propuesta

### 0:00 – 0:30 · Introducción (presentador hablando, cámara o solo voz)

> "Hola, somos el grupo [nombres]. En este video presentamos la Fase 2 del Proyecto 1
> del ramo Aprendizaje de Máquinas: un chatbot conversacional sobre mecánica
> automotriz básica, construido con un LLM local Llama 3.1 de 8 mil millones de
> parámetros, integrado mediante una arquitectura RAG sobre un corpus técnico de
> manuales y guías de mantenimiento."

### 0:30 – 1:00 · Mostrar la arquitectura

Mostrar un diagrama (puede ser una captura del README) explicando brevemente:

> "El sistema funciona en tres capas: el frontend recibe la pregunta del usuario,
> el backend FastAPI realiza la búsqueda semántica de los fragmentos más relevantes
> en una base vectorial ChromaDB, y luego envía esos fragmentos como contexto al
> modelo Llama, que genera la respuesta final."

### 1:00 – 1:30 · Mostrar la interfaz web

Capturar la pantalla con la interfaz cargada. Mostrar el panel de estado (LLM
online, RAG online, número de chunks).

> "Esta es la interfaz del chatbot. En el panel superior podemos ver el estado de
> los servicios: el LLM está activo, el motor RAG cargado, y tenemos [N] chunks
> indexados desde nuestro corpus."

### 1:30 – 6:00 · Las 10 preguntas oficiales

Hacer cada pregunta una por una. Para cada una:

1. Escribir o pegar la pregunta en la caja de chat.
2. Esperar la respuesta.
3. Comentar brevemente: ¿la respuesta fue correcta? ¿usó las fuentes adecuadas?
   ¿qué tan rápida fue?

**Tiempo aproximado por pregunta**: 25–30 segundos. Total: ~4:30 minutos.

Las 10 preguntas están en `docs/preguntas_validacion.md`.

**Tip**: si una respuesta es lenta o sale mal, mostrarla igual y comentar la
limitación. Eso aporta valor al análisis y queda profesional.

### 6:00 – 6:30 · Análisis de desempeño (resumen)

> "De las 10 preguntas evaluadas, [X] fueron respondidas de manera completa y
> correcta, [Y] tuvieron respuestas parcialmente correctas y [Z] presentaron
> limitaciones importantes. El tiempo promedio de respuesta fue de
> aproximadamente [N] segundos sobre la GTX 1060."

### 6:30 – 7:00 · Cierre

> "El detalle del análisis de cada respuesta, las limitaciones identificadas y las
> propuestas de mejora se encuentran en el informe de pruebas del repositorio.
> Gracias por la atención."

---

## Tabla para tomar notas en vivo durante la grabación

Imprime o ten esta tabla a mano mientras grabas para anotar el comportamiento
real (tiempos y observaciones). Después la usarás en el informe.

| # | Pregunta | Tiempo (ms) | Correcta (S/N/Parcial) | Observación |
|---|----------|-------------|------------------------|-------------|
| 1 | Cambio aceite sintético |  |  |  |
| 2 | Luz presión aceite |  |  |  |
| 3 | Verificar presión neumáticos |  |  |  |
| 4 | Síntomas frenos desgastados |  |  |  |
| 5 | Alineación vs balanceo |  |  |  |
| 6 | Función refrigerante |  |  |  |
| 7 | Sobrecalentamiento |  |  |  |
| 8 | Humo azul de escape |  |  |  |
| 9 | Vida útil batería |  |  |  |
| 10 | Diagnóstico alternador |  |  |  |

---

## Cómo subir el video al repositorio

GitHub no acepta archivos > 100 MB sin Git LFS. Opciones:

1. **Recomendado**: subir el video a YouTube como "no listado" y poner el link
   en el README. Es lo que esperaría el profesor.
2. Comprimir el video a < 100 MB y subirlo directo al repo en `/docs/video.mp4`.
3. Usar Git LFS (`git lfs track "*.mp4"`).

Decidir según el tamaño final del archivo.
