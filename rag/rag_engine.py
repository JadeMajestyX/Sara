import os

import chromadb
import ollama


class RAGEngine:

    def __init__(self):

        self.disabled = False
        self._warned = False

        os.environ.setdefault("CHROMA_TELEMETRY", "0")

        try:
            self.client = chromadb.PersistentClient(
                path="./rag/chroma_db"
            )

            self.collection = self.client.get_or_create_collection(
                "pdf_docs"
            )
        except Exception as error:
            self.disabled = True
            self.client = None
            self.collection = None
            print(
                "RAG deshabilitado por error al iniciar Chroma. "
                "Si necesitas RAG, respalda y borra ./rag/chroma_db. "
                f"Detalle: {error}"
            )

    def embed_query(self, text):

        if self.disabled:
            return None

        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=text
        )

        return response["embedding"]

    def search(self, query, n_results=5):

        if self.disabled:
            if not self._warned:
                print("RAG deshabilitado. Respondiendo sin contexto.")
                self._warned = True
            return ""

        query_embedding = self.embed_query(query)

        if query_embedding is None:
            return ""

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        documents = results["documents"][0]

        return "\n\n".join(documents)