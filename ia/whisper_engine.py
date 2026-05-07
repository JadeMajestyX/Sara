# ia/whisper_engine.py

import whisper


class WhisperEngine:

    def __init__(self, modelo):

        print("Cargando Whisper...")

        self.model = whisper.load_model(modelo)

    def transcribir(self, audio_path):

        print("Transcribiendo...")

        result = self.model.transcribe(
            audio_path,
            language="es"
        )

        return result["text"].strip()