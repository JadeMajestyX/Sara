from ollama import chat


class OllamaEngine:

    def __init__(self, modelo):

        self.modelo = modelo

    def preguntar(self, historial, contexto=None):

        print("Pensando...")

        mensajes = historial.copy()

        # INSERTAR CONTEXTO RAG
        if contexto:

            mensajes.insert(
                1,
                {
                    "role": "system",
                    "content": (
                        "Usa el siguiente contexto documental para responder preguntas. "
                        "Prioriza la información actual y más reciente cuando sea posible.\n\n"
                        f"{contexto}\n\n"
                        "Si el contexto contiene la respuesta, usalo. "
                        "Si el contexto no contiene la respuesta, puedes responder con tu conocimiento general. "
                        "Siempre indica si la información viene del documento o de tu conocimiento."
                    )
                }
            )

        response = chat(
            model=self.modelo,
            messages=mensajes
        )

        return response.message.content.strip()