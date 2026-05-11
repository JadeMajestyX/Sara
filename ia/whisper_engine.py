# ia/whisper_engine.py

import whisper
import torch


class WhisperEngine:

    def __init__(self, modelo, device="auto"):

        print("Cargando Whisper...")

        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        if self.device == "cuda" and not torch.cuda.is_available():
            print("CUDA no disponible. Usando CPU.")
            self.device = "cpu"

        print(f"Whisper en dispositivo: {self.device}")

        self.model = whisper.load_model(modelo, device=self.device)

    def transcribir(self, audio_path):

        print("Transcribiendo...")

        result = self.model.transcribe(
            audio_path,
            language="es",
            fp16=self.device == "cuda"
        )

        return result["text"].strip()