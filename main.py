# main.py

from config import *

from audio.recorder import AudioRecorder
from audio.speaker import Speaker

from ia.whisper_engine import WhisperEngine
from ia.ollama_engine import OllamaEngine
from rag.rag_engine import RAGEngine
from core.assistant import VoiceAssistant


def main():

    recorder = AudioRecorder(
        fs=FS,
        duracion=DURACION,
        archivo_audio=ARCHIVO_AUDIO
    )

    speaker = Speaker(
        archivo_respuesta=ARCHIVO_RESPUESTA
    )

    whisper_engine = WhisperEngine(
        modelo=MODELO_WHISPER,
        device=WHISPER_DEVICE
    )

    ia_engine = OllamaEngine(
        modelo=MODELO_IA
    )

    rag_engine = RAGEngine()

    assistant = VoiceAssistant(
        recorder=recorder,
        speaker=speaker,
        whisper_engine=whisper_engine,
        ia_engine=ia_engine,
        rag_engine=rag_engine
    )

    assistant.iniciar()


if __name__ == "__main__":
    main()