# audio/speaker.py

import asyncio
import pygame
import os
import time

import edge_tts


class Speaker:

    def __init__(
        self,
        archivo_respuesta,
        voz="es-MX-DaliaNeural"
    ):

        self.archivo_respuesta = archivo_respuesta
        self.voz = voz

        pygame.mixer.init()

    async def generar_audio(self, texto):

        communicate = edge_tts.Communicate(
            text=texto,
            voice=self.voz
        )

        await communicate.save(
            self.archivo_respuesta
        )

    def hablar(self, texto):

        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except:
            pass

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

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        try:
            pygame.mixer.music.unload()
        except:
            pass