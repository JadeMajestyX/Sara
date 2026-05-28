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


class NullAvatar:

    def mostrar_hablando(self):
        pass

    def mostrar_cerrado(self):
        pass

    def cerrar(self):
        pass

    def ejecutar(self):
        pass


def crear_avatar():

    if not SARA_USAR_AVATAR:
        return NullAvatar()

    try:
        return AvatarWindow(
            imagen_cerrada=AVATAR_CERRADO,
            imagen_hablando=AVATAR_HABLANDO
        )
    except Exception as error:
        print(f"No se pudo iniciar la ventana del avatar: {error}")
        print("Continuando sin interfaz gráfica.")
        return NullAvatar()

def main():

    avatar = crear_avatar()

    if SARA_TEXT_MODE:

        ia_engine = OllamaEngine(
            modelo=MODELO_IA
        )

        rag_engine = RAGEngine()

        assistant = VoiceAssistant(
            recorder=None,
            speaker=None,
            whisper_engine=None,
            ia_engine=ia_engine,
            rag_engine=rag_engine,
            on_finish=avatar.cerrar
        )

        assistant.iniciar_texto()
        return

    recorder = AudioRecorder(
        fs=FS,
        archivo_audio=ARCHIVO_AUDIO,
        chunk_ms=CHUNK_MS,
        umbral_voz=UMBRAL_VOZ,
        silencio_maximo=SILENCIO_MAXIMO,
        min_habla_ms=MIN_HABLA_MS
    )

    speaker = Speaker(
        archivo_respuesta=ARCHIVO_RESPUESTA,
        on_start_speaking=avatar.mostrar_hablando,
        on_stop_speaking=avatar.mostrar_cerrado
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
        rag_engine=rag_engine,
        on_finish=avatar.cerrar
    )

    hilo_asistente = Thread(target=assistant.iniciar, daemon=True)
    hilo_asistente.start()

    avatar.ejecutar()

    hilo_asistente.join(timeout=1)


if __name__ == "__main__":
    main()