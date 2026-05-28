# main.py

from config import *

from audio.recorder import AudioRecorder
from audio.speaker import Speaker

from ia.whisper_engine import WhisperEngine
from ia.ollama_engine import OllamaEngine
from rag.rag_engine import RAGEngine
from core.assistant import VoiceAssistant
from ui.avatar_window import AvatarWindow

from threading import Thread

def main():

    print("Iniciando ventana de avatar...", flush=True)

    avatar = AvatarWindow(
        imagen_cerrada=AVATAR_CERRADO,
        imagen_hablando=AVATAR_HABLANDO
    )

    print("Iniciando grabadora de audio...", flush=True)

    recorder = AudioRecorder(
        fs=FS,
        archivo_audio=ARCHIVO_AUDIO,
        device=INPUT_DEVICE,
        chunk_ms=CHUNK_MS,
        umbral_voz=UMBRAL_VOZ,
        silencio_maximo=SILENCIO_MAXIMO,
        min_habla_ms=MIN_HABLA_MS
    )

    print("Iniciando sintetizador de voz...", flush=True)

    speaker = Speaker(
        archivo_respuesta=ARCHIVO_RESPUESTA,
        on_start_speaking=avatar.mostrar_hablando,
        on_stop_speaking=avatar.mostrar_cerrado
    )

    print("Cargando Whisper...", flush=True)

    whisper_engine = WhisperEngine(
        modelo=MODELO_WHISPER,
        device=WHISPER_DEVICE
    )

    print("Inicializando motor IA...", flush=True)

    ia_engine = OllamaEngine(
        modelo=MODELO_IA
    )

    print("Inicializando RAG...", flush=True)

    rag_engine = RAGEngine()

    assistant = VoiceAssistant(
        recorder=recorder,
        speaker=speaker,
        whisper_engine=whisper_engine,
        ia_engine=ia_engine,
        rag_engine=rag_engine,
        on_finish=avatar.cerrar
    )

    hilo_asistente = Thread(target=assistant.iniciar, daemon=True)
    hilo_asistente.start()

    avatar.ejecutar()

    hilo_asistente.join(timeout=1)


if __name__ == "__main__":
    main()