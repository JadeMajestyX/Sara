# audio/speaker.py

import asyncio
import pygame
import os
import time
import re
import numpy as np
import threading

import pyttsx3


class Speaker:

    def __init__(
        self,
        archivo_respuesta,
        voz="es-MX-DaliaNeural",
        on_start_speaking=None,
        on_stop_speaking=None
    ):

        self.archivo_respuesta = archivo_respuesta
        self.voz = voz
        self.on_start_speaking = on_start_speaking
        self.on_stop_speaking = on_stop_speaking
        self._detener_evento = threading.Event()

        pygame.mixer.init()

        self.engine = pyttsx3.init()

        self.engine.setProperty('rate', 170)

        self.engine.setProperty('volume', 1.0)

    def _avisar_estado(self, hablando):

        callback = self.on_start_speaking if hablando else self.on_stop_speaking

        if callback is not None:

            try:
                callback()
            except:
                pass

    def detener(self):

        self._detener_evento.set()

        try:
            pygame.mixer.music.stop()
        except:
            pass

        self._avisar_estado(False)

    def _limpiar_texto_para_voz(self, texto):

        texto = re.sub(r"[*_`#>~]", "", texto)
        texto = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", texto)
        texto = re.sub(
            r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF]",
            "",
            texto
        )
        texto = re.sub(r"\s+", " ", texto)

        return texto.strip()

    async def generar_audio(self, texto):

        texto = self._limpiar_texto_para_voz(texto)

        comando = (
            f'echo "{texto}" | '
            f'"C:\\tesis\\Sara\\piper\\piper.exe" '
            f'--model "C:\\tesis\\Sara\\voices\\es_MX-claude-high.onnx" '
            f'--output_file "{self.archivo_respuesta}"'
        )

        os.system(comando)

    def _perfil_actividad_audio(self, chunk_ms=120):

        try:
            sonido = pygame.mixer.Sound(self.archivo_respuesta)
            muestras = pygame.sndarray.array(sonido)
        except:
            return [], chunk_ms

        if muestras is None or getattr(muestras, "size", 0) == 0:
            return [], chunk_ms

        amplitud = np.abs(muestras.astype(np.float32))

        if amplitud.ndim > 1:
            amplitud = amplitud.mean(axis=1)

        mixer_info = pygame.mixer.get_init()
        sample_rate = mixer_info[0] if mixer_info else 44100
        chunk_samples = max(1, int(sample_rate * chunk_ms / 1000))

        energia_chunks = []

        for inicio in range(0, len(amplitud), chunk_samples):
            chunk = amplitud[inicio:inicio + chunk_samples]

            if chunk.size == 0:
                energia_chunks.append(0.0)
                continue

            rms = float(np.sqrt(np.mean(chunk * chunk)))
            energia_chunks.append(rms)

        if not energia_chunks:
            return [], chunk_ms

        energia_max = max(energia_chunks)
        umbral = max(250.0, energia_max * 0.08)
        actividad = [energia >= umbral for energia in energia_chunks]

        for i in range(1, len(actividad) - 1):
            if not actividad[i] and actividad[i - 1] and actividad[i + 1]:
                actividad[i] = True

        for i in range(1, len(actividad) - 1):
            if actividad[i] and not actividad[i - 1] and not actividad[i + 1]:
                actividad[i] = False

        return actividad, chunk_ms

    def hablar(self, texto):

        self._detener_evento.clear()

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except:
            pass

        try:
            time.sleep(0.2)

            if os.path.exists(self.archivo_respuesta):

                try:
                    os.remove(self.archivo_respuesta)
                except:
                    pass

            # Generar voz
            asyncio.run(
                self.generar_audio(texto)
            )

            # Reproducir
            pygame.mixer.music.load(
                self.archivo_respuesta
            )

            actividad_audio, chunk_ms = self._perfil_actividad_audio()
            ultimo_estado = False

            self._avisar_estado(False)

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():

                if self._detener_evento.is_set():

                    pygame.mixer.music.stop()
                    break

                estado_actual = False

                if actividad_audio:
                    pos_ms = pygame.mixer.music.get_pos()

                    if pos_ms >= 0:
                        idx = min(len(actividad_audio) - 1, pos_ms // chunk_ms)
                        estado_actual = actividad_audio[idx]

                if estado_actual != ultimo_estado:
                    self._avisar_estado(estado_actual)
                    ultimo_estado = estado_actual

                time.sleep(0.05)
        finally:
            try:
                pygame.mixer.music.unload()
            except:
                pass

            self._avisar_estado(False)