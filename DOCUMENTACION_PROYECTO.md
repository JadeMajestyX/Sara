# Documentación del Proyecto

Este documento describe el proyecto desarrollado por Jose Angel Alvarez Carranza y Sandra Vannesa Rodriguez Arechiga para la tesis. Contiene descripción de la arquitectura, componentes, flujo de datos, configuración, instalación y anexos con referencias a los archivos clave.

---

## Resumen

El proyecto es un asistente de voz en español orientado a la Facultad de Ingeniería Electromecánica (FIE) de la Universidad de Colima. Combina entrada de audio (grabación), transcripción con Whisper, generación de respuestas con Ollama (chat) y recuperación de documentos (RAG) mediante ChromaDB y embeddings proporcionados por Ollama.

## Objetivos

- Proveer un asistente de voz conversacional en español.
- Integrar transcripción automática, búsqueda de contexto documental y generación de respuestas coherentes.
- Facilitar la ingestión de documentos PDF para responder consultas basadas en documentos de la facultad.

## Estructura del repositorio

- `config.py`: Configuración global (frecuencia de muestreo, duración, modelos, rutas de archivos).
- `main.py`: Punto de entrada; instancia componentes y arranca el asistente.
- `audio/recorder.py`: Clase `AudioRecorder` para grabar audio desde el micrófono.
- `audio/speaker.py`: Clase `Speaker` que genera voz con `edge_tts` y reproduce con `pygame`.
- `core/assistant.py`: `VoiceAssistant` que orquesta el flujo de grabación, transcripción, RAG y generación de respuesta.
- `ia/whisper_engine.py`: `WhisperEngine` que carga el modelo Whisper y transcribe audio.
- `ia/ollama_engine.py`: `OllamaEngine` que hace llamadas al API de Ollama para chat y embeddings.
- `rag/ingest.py`: Utilidades para extraer texto de PDFs, fragmentarlo, crear embeddings y guardarlos en ChromaDB.
- `rag/retriever.py`: Funciones auxiliares de búsqueda RAG sobre la base de datos local.
- `rag/rag_engine.py`: Clase `RAGEngine` que encapsula la búsqueda por embeddings y recuperación de documentos.
- `requirements.txt`: Dependencias del proyecto.

## Componentes y descripción técnica

### Configuración (`config.py`)

Parámetros principales:

- `FS` (int): frecuencia de muestreo, por defecto 16000.
- `DURACION` (int): segundos de grabación por turno.
- `MODELO_WHISPER` (str): nombre del modelo Whisper a cargar.
- `MODELO_IA` (str): modelo utilizado por Ollama para chat.
- `WHISPER_DEVICE` (str): dispositivo para Whisper (`cuda`/`cpu`/`auto`).
- `ARCHIVO_AUDIO` y `ARCHIVO_RESPUESTA`: rutas temporales para audio.

Ver: [config.py](config.py#L1-L20)

### Entrada de audio (`audio/recorder.py`)

Clase `AudioRecorder`:

- Usa `sounddevice` para grabar audio mono en formato `int16`.
- Muestra un conteo regresivo durante la grabación y guarda un archivo WAV.

Ver: [audio/recorder.py](audio/recorder.py#L1-L100)

### Salida de audio (`audio/speaker.py`)

Clase `Speaker`:

- Genera audio TTS mediante `edge_tts.Communicate` y lo guarda en `temp/respuesta.mp3`.
- Reproduce audio con `pygame.mixer` y espera a que termine la reproducción.

Ver: [audio/speaker.py](audio/speaker.py#L1-L200)

### Transcripción (`ia/whisper_engine.py`)

Clase `WhisperEngine`:

- Carga un modelo Whisper mediante `whisper.load_model(modelo, device)`.
- Método `transcribir(audio_path)` que devuelve el texto transcrito en español.

Ver: [ia/whisper_engine.py](ia/whisper_engine.py#L1-L200)

### Motor de IA (`ia/ollama_engine.py`)

Clase `OllamaEngine`:

- Envía `messages` al servicio `ollama.chat` para obtener respuestas.
- Si se provee `contexto` (desde RAG), lo inserta como `system` message para priorizar la información documental.

Ver: [ia/ollama_engine.py](ia/ollama_engine.py#L1-L200)

### Recuperación y RAG (`rag/`) 

- `rag/ingest.py`: Extracción de texto desde PDF (`pypdf.PdfReader`), fragmentación en chunks, creación de embeddings con `ollama.embeddings` y almacenamiento en `chromadb.PersistentClient`.
- `rag/rag_engine.py` y `rag/retriever.py`: Funciones y clase para consultar la base de datos por similitud usando embeddings y devolver fragmentos relevantes.

Ver: [rag/ingest.py](rag/ingest.py#L1-L400) y [rag/rag_engine.py](rag/rag_engine.py#L1-L200)

### Core: Orquestador (`core/assistant.py`)

Clase `VoiceAssistant`:

- Mantiene un `historial` inicial con instrucciones de sistema (tono, público objetivo, limitaciones de respuesta y autores).
- Bucle principal (`iniciar()`): graba audio, transcribe, si el texto no es vacío añade al historial, consulta RAG por contexto, solicita respuesta a la IA y reproduce la respuesta.
- Detección de comandos de salida (`es_comando_salida`).

Ver: [core/assistant.py](core/assistant.py#L1-L400)

## Flujo de ejecución (alto nivel)

1. `main.py` instancia:
   - `AudioRecorder`, `Speaker`, `WhisperEngine`, `OllamaEngine`, `RAGEngine` y `VoiceAssistant`.
2. `VoiceAssistant.iniciar()` comienza el bucle interactivo.
3. Para cada turno:
   - Grabar audio -> guardar WAV.
   - Transcribir WAV -> obtener texto.
   - Buscar contexto relevante en RAG -> obtener documentos/chunks.
   - Enviar historial + contexto a Ollama -> obtener respuesta.
   - Reproducir respuesta con TTS.

Ver: [main.py](main.py#L1-L200)

## Instalación y ejecución

Recomendado crear un entorno virtual y luego instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\Activate.ps1 en Windows PowerShell
pip install -r requirements.txt
```

Para ejecutar el asistente:

```bash
python main.py
```

Para ingestar un PDF manualmente:

```bash
python rag/ingest.py ruta/al/documento.pdf
```

## Consideraciones técnicas y dependencias

- Requiere acceso a micrófono y salida de audio en el sistema.
- `whisper` y `torch` pueden requerir CUDA/configuración para GPU.
- `edge_tts` usa servicios de síntesis de Microsoft (ver compatibilidad).
- `chromadb` utiliza una base persistente en `./rag/chroma_db`.

Ver: [requirements.txt](requirements.txt)

## Limitaciones conocidas

- El asistente depende de la calidad de la transcripción de Whisper.
- Ollama y Ollama embeddings requieren el servicio/daemon de Ollama correctamente configurado.
- Manejo de errores y excepciones es básico en varias partes (por ejemplo, interacción con servicios externos).

## Buenas prácticas y recomendaciones para tesis

- Documentar los experimentos con diferentes modelos de `MODELO_WHISPER` y `MODELO_IA`.
- Medir métricas: latencia por turno, tasa de error de transcripción (WER), precisión en respuestas basadas en documentos.
- Anotar versiones exactas en `requirements.txt` para reproducibilidad.

## Contribuciones y créditos

- Autores: Jose Angel Alvarez Carranza y Sandra Vannesa Rodriguez Arechiga.

## Anexos

- Archivos clave:
  - [config.py](config.py#L1-L20)
  - [main.py](main.py#L1-L200)
  - [core/assistant.py](core/assistant.py#L1-L400)
  - [audio/recorder.py](audio/recorder.py#L1-L200)
  - [audio/speaker.py](audio/speaker.py#L1-L300)
  - [ia/whisper_engine.py](ia/whisper_engine.py#L1-L200)
  - [ia/ollama_engine.py](ia/ollama_engine.py#L1-L200)
  - [rag/ingest.py](rag/ingest.py#L1-L400)

---

Si deseas, puedo:

- Generar una versión en LaTeX compatible con una plantilla de tesis.
- Incluir fragmentos de código completos y extraer diagramas de arquitectura.
- Añadir métricas sugeridas y plantillas para experimentos.
