# audio/recorder.py

import threading
import time

import numpy as np
import sounddevice as sd

from scipy.io.wavfile import write


class AudioRecorder:

    def __init__(
        self,
        fs,
        archivo_audio,
        chunk_ms=100,
        umbral_voz=650,
        silencio_maximo=1.0,
        min_habla_ms=200
    ):

        self.fs = fs
        self.archivo_audio = archivo_audio
        self.chunk_ms = chunk_ms
        self.umbral_voz = umbral_voz
        self.silencio_maximo = silencio_maximo
        self.min_habla_ms = min_habla_ms
        self.chunk_samples = max(1, int(self.fs * self.chunk_ms / 1000))

    def _energia(self, chunk):

        datos = chunk.astype(np.float32)

        if datos.ndim > 1:
            datos = datos.mean(axis=1)

        return float(np.sqrt(np.mean(datos * datos))) if datos.size else 0.0

    def _guardar_audio(self, fragmentos):

        audio = np.concatenate(fragmentos, axis=0)
        write(self.archivo_audio, self.fs, audio)
        return self.archivo_audio

    def start_listening(self, on_utterance, on_speech_start=None, on_speech_end=None, stop_event=None):

        if stop_event is None:
            stop_event = threading.Event()

        hilo = threading.Thread(
            target=self._escuchar_continuo,
            args=(on_utterance, on_speech_start, on_speech_end, stop_event),
            daemon=True
        )
        hilo.start()

        return hilo, stop_event

    def _escuchar_continuo(self, on_utterance, on_speech_start, on_speech_end, stop_event):

        print("\nEscuchando...")

        prebuffer = []
        max_prebuffer = max(1, int(300 / self.chunk_ms))
        silencio_limite = max(1, int(self.silencio_maximo * 1000 / self.chunk_ms))
        min_habla_chunks = max(1, int(self.min_habla_ms / self.chunk_ms))

        grabando = False
        energia_activa = 0
        energia_silencio = 0
        fragmentos = []

        try:
            with sd.InputStream(
                samplerate=self.fs,
                channels=1,
                dtype="int16",
                blocksize=self.chunk_samples
            ) as stream:

                while not stop_event.is_set():

                    chunk, _ = stream.read(self.chunk_samples)

                    if chunk.size == 0:
                        continue

                    energia = self._energia(chunk)
                    hay_voz = energia >= self.umbral_voz

                    if not grabando:

                        prebuffer.append(chunk.copy())

                        if len(prebuffer) > max_prebuffer:
                            prebuffer.pop(0)

                        if hay_voz:
                            energia_activa += 1
                        else:
                            energia_activa = 0

                        if energia_activa >= min_habla_chunks:

                            grabando = True
                            energia_silencio = 0
                            fragmentos = list(prebuffer)

                            if on_speech_start is not None:

                                try:
                                    on_speech_start()
                                except:
                                    pass

                    else:

                        fragmentos.append(chunk.copy())

                        if hay_voz:
                            energia_silencio = 0
                        else:
                            energia_silencio += 1

                        if energia_silencio >= silencio_limite:

                            if len(fragmentos) > energia_silencio:
                                fragmentos = fragmentos[:-energia_silencio]

                            if fragmentos:
                                try:
                                    audio_path = self._guardar_audio(fragmentos)
                                    on_utterance(audio_path)
                                except:
                                    pass

                            if on_speech_end is not None:

                                try:
                                    on_speech_end()
                                except:
                                    pass

                            grabando = False
                            energia_activa = 0
                            energia_silencio = 0
                            fragmentos = []
                            prebuffer = []

        except Exception as error:
            print(f"Error en el escucha continua: {error}")