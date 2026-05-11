import chromadb
import ollama


class RAGEngine:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./rag/chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            "pdf_docs"
        )

    def embed_query(self, text):

        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=text
        )

        return response["embedding"]

    def search(self, query, n_results=5):

        query_embedding = self.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        documents = results["documents"][0]

        return "\n\n".join(documents)