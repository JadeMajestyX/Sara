# core/assistant.py

class VoiceAssistant:

    def __init__(
        self,
        recorder,
        speaker,
        whisper_engine,
        ia_engine
    ):

        self.recorder = recorder
        self.speaker = speaker
        self.whisper = whisper_engine
        self.ia = ia_engine

        self.historial = [
            {
                "role": "system",
                "content": (
                    "Eres una asistente virtual en español."
                    "Responde breve y claro."
                    "Eres una asistente carismatico, amigable y servicial."
                    "Debes de responder con información oficial y verificada."
                    "No debes inventar información, si no sabes algo, di que no lo sabes."
                    "Eres una asistente inteligente de la Universidad de Colima, de la Facultad de Ingenieria Electromecanica (FIE)."
                    "Puedes responder cualquier pregunta, pero siempre debes de relacionar tus respuestas con la Universidad de Colima y la Facultad de Ingenieria Electromecanica (FIE)."
                    "Las carreras que se imparten en la Facultad de Ingenieria Electromecanica (FIE) son: Ingeniería de Software, Ingeniería en Mecatrónica, Ingeniería en Tecnologías Electrónicas, Ingeniero Mecánico Electricista, Maestría en Ingeniería Aplicada"
                )
            }
        ]

    def es_comando_salida(self, texto):

        comandos = [
            "salir",
            "terminar",
            "adiós",
            "adios"
        ]

        return texto.lower() in comandos

    def iniciar(self):

        print("\nAsistente iniciado.\n")

        self.speaker.hablar(
            "Hola, soy tu asistente virtual."
        )

        while True:

            audio_path = self.recorder.grabar()

            texto = self.whisper.transcribir(audio_path)

            if not texto:

                print("No se detectó voz.")
                continue

            print("\nTú:", texto)

            if self.es_comando_salida(texto):

                despedida = "Hasta luego."

                print("\nIA:", despedida)

                self.speaker.hablar(despedida)

                break

            self.historial.append({
                "role": "user",
                "content": texto
            })

            respuesta = self.ia.preguntar(
                self.historial
            )

            print("\nIA:", respuesta)

            self.historial.append({
                "role": "assistant",
                "content": respuesta
            })

            self.speaker.hablar(respuesta)