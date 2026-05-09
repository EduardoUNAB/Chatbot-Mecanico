# Slide de Dominio — Fase 2

**Para incluir en la presentación de la Fase 1 (junto al resto del informe).**

---

## Contenido propuesto del slide

### Título principal
**Dominio del Chatbot — Fase 2**
Mecánica Automotriz Básica y Mantenimiento Preventivo

### Punto 1 — Definición del dominio
Asistente conversacional que orienta a usuarios comunes, sin conocimientos
técnicos avanzados, sobre el cuidado, los componentes y el funcionamiento
básico de un vehículo de pasajeros.

### Punto 2 — Justificación de la elección

Cuatro razones por las que se eligió este dominio:

1. **Relevancia social.** El parque automotor de Chile supera los 6 millones de
   vehículos. La inmensa mayoría de propietarios carece de formación técnica y
   recurre a internet o a consultas informales para mantenimiento básico.

2. **Conocimiento estructurado y abundante.** Existe vasta documentación pública
   en manuales de fabricante, normas técnicas (SAG, plantas de revisión técnica)
   y guías de componentistas (Bosch, NGK, Castrol). Esto facilita la
   construcción de un corpus de calidad para RAG.

3. **No depende de informática.** Cumple el requisito del enunciado de elegir un
   dominio fuera del área de computación.

4. **Demanda real validada.** Las consultas de mantenimiento básico son uno de
   los temas más buscados en español en plataformas como YouTube y foros
   automotrices, lo que valida la utilidad práctica de la solución.

### Punto 3 — Alcance acotado
El chatbot se limita a información preventiva y educativa. NO realiza
diagnósticos clínicos del vehículo ni reemplaza el criterio de un mecánico
profesional, lo cual está explicitado en el prompt del sistema y en la interfaz.

### Punto 4 — Arquitectura técnica
- LLM local: Llama 3.1 8B (Q4_K_M) vía Ollama
- RAG: ChromaDB + sentence-transformers multilingual
- Backend: FastAPI · Frontend: HTML + JavaScript

### Punto 5 — Validación
10 preguntas técnicas representativas del dominio (cambio de aceite, luces del
tablero, frenos, sistema de refrigeración, batería, alternador, neumáticos,
alineación/balanceo y diagnóstico por color de escape) cubriendo los 5 sistemas
fundamentales del vehículo.

---

## Sugerencia visual

Usar una sola imagen central potente: silueta o diagrama de un vehículo con
íconos sobre los 5 sistemas que cubre el corpus (motor, frenos, neumáticos,
refrigeración, eléctrico). En las esquinas, las 4 razones de la elección
en bullets cortos.

Paleta sugerida: gris oscuro / naranja para coherencia con la UI del chatbot.
