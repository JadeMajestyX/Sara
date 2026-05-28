# core/assistant.py

import re


class VoiceAssistant:

    def __init__(
        self,
        recorder,
        speaker,
        whisper_engine,
        ia_engine,
        rag_engine,
        on_finish=None
    ):

        self.recorder = recorder
        self.speaker = speaker
        self.whisper = whisper_engine
        self.ia = ia_engine
        self.rag = rag_engine
        self.on_finish = on_finish

        self.historial = [
            {
                "role": "system",
                "content": (
                    "Eres una asistente virtual en español. "
                    "Responde breve, claro y con tono amigable. "
                    "No utilices emojis. "
                    "No inventes información: si no sabes algo, dilo con honestidad. "
                    "Habla de frente, como si estuvieras conversando con el usuario. "
                    "Actúas como una secretaria/asistente administrativa: orientas, informas y apoyas en temas institucionales y de atención. "
                    "No puedes enseñar programación ni responder solicitudes técnicas de código. "
                    "Si te piden código o temas de programación, rechaza la solicitud de forma breve y redirige a temas de orientación académica o administrativa. "
                    "Tus respuestas se escuchan por voz, así que deben ser fáciles de entender. "
                    "Eres una asistente inteligente de la Universidad de Colima, de la Facultad de Ingeniería Electromecánica (FIE). "
                    "Relaciona tus respuestas con la Universidad de Colima y la Facultad de Ingeniería Electromecánica (FIE) cuando sea pertinente. "
                    "Las carreras que se imparten en la Facultad de Ingeniería Electromecánica (FIE) son: Ingeniería de Software, Ingeniería en Mecatrónica, Ingeniería en Tecnologías Electrónicas, Ingeniero Mecánico Electricista y Maestría en Ingeniería Aplicada. "
                    "Tus creadores son los alumnos Jose Angel Alvarez Carranza y Sandra Vannesa Rodriguez Arechiga."
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

    def es_consulta_codigo(self, texto):

        texto_normalizado = texto.lower()

        patrones = [
            r"\bc[oó]digo\b",
            r"\bprogramaci[oó]n\b",
            r"\bprogramar\b",
            r"\bscript\b",
            r"\balgoritmo\b",
            r"\bjava\b",
            r"\bpython\b",
            r"\bc\+\+\b",
            r"\bc#\b",
            r"\bjavascript\b",
            r"\bhtml\b",
            r"\bcss\b",
            r"\bsql\b",
            r"\bapi\b",
            r"\bfunci[oó]n\b",
            r"\bclase\b",
            r"\bdepurar\b",
            r"\bcompilar\b",
            r"\bhola mundo\b",
            r"\bhello world\b"
        ]

        return any(re.search(patron, texto_normalizado) for patron in patrones)

    def iniciar(self):

        if self.recorder is None or self.speaker is None or self.whisper is None:
            raise RuntimeError(
                "Faltan componentes de voz. Usa iniciar_texto() para modo sin audio."
            )

        try:
            print("\nAsistente iniciado.\n")

            audio_queue = __import__("queue").Queue()
            stop_event = __import__("threading").Event()

            self.recorder.start_listening(
                on_utterance=audio_queue.put,
                on_speech_start=self.speaker.detener,
                stop_event=stop_event
            )

            self.speaker.hablar(
                "Hola, estoy aqui para resolver tus dudas acerca de la facultad."
            )

            while True:

                audio_path = audio_queue.get()

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

                if self.es_consulta_codigo(texto):

                    respuesta = (
                        "No puedo ayudar con programación o código. "
                        "Puedo apoyarte como asistente en orientación académica y administrativa de la facultad."
                    )

                    print("\nIA:", respuesta)

                    self.historial.append({
                        "role": "user",
                        "content": texto
                    })

                    self.historial.append({
                        "role": "assistant",
                        "content": respuesta
                    })

                    self.speaker.hablar(respuesta)
                    continue

                self.historial.append({
                    "role": "user",
                    "content": texto
                })

                contexto = self.rag.search(texto)

                respuesta = self.ia.preguntar(
                    self.historial,
                    contexto=contexto
                )

                print("\nIA:", respuesta)

                self.historial.append({
                    "role": "assistant",
                    "content": respuesta
                })

                self.speaker.hablar(respuesta)
        finally:
            try:
                stop_event.set()
            except:
                pass

            if self.on_finish is not None:
                try:
                    self.on_finish()
                except:
                    pass

    def iniciar_texto(self):

        print("\nAsistente iniciado en modo texto.\n")
        print("Escribe tu consulta. Usa 'salir' para terminar.")

        try:
            while True:

                try:
                    texto = input("\nTú: ").strip()
                except EOFError:
                    texto = "salir"

                if not texto:
                    continue

                if self.es_comando_salida(texto):

                    despedida = "Hasta luego."
                    print("\nIA:", despedida)
                    break

                if self.es_consulta_codigo(texto):

                    respuesta = (
                        "No puedo ayudar con programación o código. "
                        "Puedo apoyarte como asistente en orientación académica y administrativa de la facultad."
                    )

                    print("\nIA:", respuesta)

                    self.historial.append({
                        "role": "user",
                        "content": texto
                    })

                    self.historial.append({
                        "role": "assistant",
                        "content": respuesta
                    })

                    continue

                self.historial.append({
                    "role": "user",
                    "content": texto
                })

                contexto = self.rag.search(texto)

                respuesta = self.ia.preguntar(
                    self.historial,
                    contexto=contexto
                )

                print("\nIA:", respuesta)

                self.historial.append({
                    "role": "assistant",
                    "content": respuesta
                })
        finally:
            if self.on_finish is not None:
                try:
                    self.on_finish()
                except:
                    pass