# audio/recorder.py

import sounddevice as sd
import time

from scipy.io.wavfile import write


class AudioRecorder:

    def __init__(self, fs, duracion, archivo_audio):

        self.fs = fs
        self.duracion = duracion
        self.archivo_audio = archivo_audio

    def grabar(self):

        print("\nHabla ahora...")

        audio = sd.rec(
            int(self.duracion * self.fs),
            samplerate=self.fs,
            channels=1,
            dtype="int16"
        )

        for i in range(self.duracion, 0, -1):
            print(f"\rTiempo restante: {i} segundos ", end="")
            time.sleep(1)

        sd.wait()

        print("\nGrabación terminada.")

        write(self.archivo_audio, self.fs, audio)

        return self.archivo_audio