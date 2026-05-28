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

        try:
            if not audio_path:
                return ""
        except Exception:
            return ""

        try:
            result = self.model.transcribe(
                audio_path,
                language="es",
                fp16=self.device == "cuda",
                temperature=0.0,
                beam_size=5,
                best_of=5,
                condition_on_previous_text=False,
                no_speech_threshold=0.55,
                logprob_threshold=-1.0,
                compression_ratio_threshold=2.4,
                initial_prompt=(
                    "Transcribe en español con precisión. "
                    "Conserva nombres propios, tecnicismos y frases cortas tal como se escuchan."
                )
            )
        except RuntimeError as error:
            print(f"No se pudo transcribir el audio: {error}")
            return ""

        return result["text"].strip()