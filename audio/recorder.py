# audio/recorder.py

import os
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
        device=None,
        chunk_ms=100,
        umbral_voz=650,
        silencio_maximo=1.0,
        min_habla_ms=200
    ):

        self.fs = fs
        self.archivo_audio = archivo_audio
        self.device = device
        self.chunk_ms = chunk_ms
        self.umbral_voz = umbral_voz
        self.silencio_maximo = silencio_maximo
        self.min_habla_ms = min_habla_ms
        self.chunk_samples = max(1, int(self.fs * self.chunk_ms / 1000))
        self.debug_audio = os.getenv("DEBUG_AUDIO") == "1"

    def _energia(self, chunk):

        datos = chunk.astype(np.float32)

        if datos.ndim > 1:
            datos = datos.mean(axis=1)

        return float(np.sqrt(np.mean(datos * datos))) if datos.size else 0.0

    def _guardar_audio(self, fragmentos):

        audio = np.concatenate(fragmentos, axis=0)
        write(self.archivo_audio, self.fs, audio)
        return self.archivo_audio

    def _candidatos_stream(self):

        device_candidates = []
        if self.device is not None:
            device_candidates.append(self.device)
        if None not in device_candidates:
            device_candidates.append(None)

        samplerates = []

        for dev in device_candidates:
            try:
                info = sd.query_devices(
                    dev if dev is not None else sd.default.device[0],
                    "input"
                )
            except Exception:
                info = None

            if info and info.get("default_samplerate"):
                samplerates.append(int(info["default_samplerate"]))

        samplerates.extend([self.fs, 48000, 44100, 16000])

        seen = set()
        sr_candidates = []
        for sr in samplerates:
            if sr and sr not in seen:
                sr_candidates.append(sr)
                seen.add(sr)

        for dev in device_candidates:
            for sr in sr_candidates:
                blocksize = max(1, int(sr * self.chunk_ms / 1000))
                for bs in (blocksize, None):
                    params = {
                        "samplerate": sr,
                        "channels": 1,
                        "dtype": "int16"
                    }
                    if dev is not None:
                        params["device"] = dev
                    if bs is not None:
                        params["blocksize"] = bs
                    yield params

    def _abrir_stream(self):

        last_error = None

        for params in self._candidatos_stream():
            try:
                sd.check_input_settings(
                    device=params.get("device"),
                    samplerate=params["samplerate"],
                    channels=params["channels"],
                    dtype=params["dtype"]
                )
            except Exception as error:
                last_error = error
                if self.debug_audio:
                    print(f"Settings invalidos: {params} -> {error}")
                continue

            try:
                stream = sd.InputStream(**params)
                stream.start()
                if self.debug_audio:
                    print(f"Iniciando InputStream: {params}")
                return stream, params
            except Exception as error:
                last_error = error
                if self.debug_audio:
                    print(f"Fallo InputStream: {params} -> {error}")
                try:
                    stream.close()
                except Exception:
                    pass

        raise RuntimeError(
            f"No se pudo abrir entrada de audio. Ultimo error: {last_error}"
        )

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

        try:
            stream, params = self._abrir_stream()
        except Exception as error:
            print(f"Error en el escucha continua: {error}")
            return

        self.fs = int(params["samplerate"])
        self.chunk_samples = max(1, int(self.fs * self.chunk_ms / 1000))

        prebuffer = []
        max_prebuffer = max(1, int(300 / self.chunk_ms))
        silencio_limite = max(1, int(self.silencio_maximo * 1000 / self.chunk_ms))
        min_habla_chunks = max(1, int(self.min_habla_ms / self.chunk_ms))

        grabando = False
        energia_activa = 0
        energia_silencio = 0
        fragmentos = []

        if self.debug_audio:
            dispositivo = params.get("device")
            print(f"Usando dispositivo de entrada: {dispositivo}")

        ultimo_log = time.time()

        try:
            while not stop_event.is_set():

                chunk, _ = stream.read(self.chunk_samples)

                if chunk.size == 0:
                    continue

                energia = self._energia(chunk)
                hay_voz = energia >= self.umbral_voz

                if self.debug_audio and time.time() - ultimo_log >= 1.0:
                    print(f"Energia={energia:.1f} Umbral={self.umbral_voz} Voz={hay_voz}")
                    ultimo_log = time.time()

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
        finally:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass