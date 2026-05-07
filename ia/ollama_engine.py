# ia/ollama_engine.py

from ollama import chat


class OllamaEngine:

    def __init__(self, modelo):

        self.modelo = modelo

    def preguntar(self, historial):

        print("Pensando...")

        response = chat(
            model=self.modelo,
            messages=historial
        )

        return response.message.content.strip()