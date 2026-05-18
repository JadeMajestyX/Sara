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
                        "Usa el siguiente contexto como apoyo para responder. "
                        "Prioriza la información actual y reciente cuando sea posible.\n\n"
                        f"{contexto}\n\n"
                        "Si el contexto contiene la respuesta, úsalo. "
                        "Si el contexto no contiene la respuesta, responde de forma directa con lo que sí sabes o di que no lo sabes. "
                        "No menciones documentos, búsquedas ni el origen de la información."
                    )
                }
            )

        response = chat(
            model=self.modelo,
            messages=mensajes
        )

        return response.message.content.strip()