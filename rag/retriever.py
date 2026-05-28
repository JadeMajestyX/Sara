import os

os.environ.setdefault("CHROMA_TELEMETRY", "0")

import chromadb
import ollama

try:
    client = chromadb.PersistentClient(path="./rag/chroma_db")
    collection = client.get_or_create_collection("pdf_docs")
except Exception as error:
    raise SystemExit(
        "Error al iniciar Chroma. Respaldar y borrar ./rag/chroma_db y reintentar. "
        f"Detalle: {error}"
    )


def embed_query(text):
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )

    return response["embedding"]


def search(query, n_results=3):
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0]