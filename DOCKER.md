# Docker: Ejecucion multiplataforma

Esta configuracion permite ejecutar el proyecto en Windows, Linux o macOS con Docker Desktop y Docker Compose.

## 1) Construir y levantar servicios

```bash
docker compose up -d --build
```

Esto levanta:
- `ollama` en `http://localhost:11434`
- `assistant` en modo texto dentro del contenedor

## 2) Descargar modelos en Ollama (una sola vez)

```bash
docker compose exec ollama ollama pull gemma2:2b
docker compose exec ollama ollama pull nomic-embed-text
```

## 3) Ejecutar el asistente en modo interactivo

```bash
docker compose run --rm assistant
```

Escribe tus consultas en consola. Para salir, usa `salir`.

## 4) Ingestar documentos PDF para RAG

Coloca PDFs en `docs/` y ejecuta:

```bash
docker compose run --rm assistant python rag/ingest.py ./docs/tu_documento.pdf
```

## 5) Apagar servicios

```bash
docker compose down
```

## Variables utiles

Estas variables ya vienen definidas en `docker-compose.yml`:
- `OLLAMA_HOST=http://ollama:11434`
- `WHISPER_DEVICE=cpu`
- `SARA_TEXT_MODE=1`
- `SARA_USAR_AVATAR=0`

Puedes cambiarlas para ajustar comportamiento.

## Notas importantes

- La configuracion Docker esta optimizada para modo texto/headless (estable en cualquier PC).
- Si quieres usar microfono, audio y avatar GUI, es mejor ejecutar localmente sin contenedor o preparar passthrough de audio/display especifico por sistema operativo.
