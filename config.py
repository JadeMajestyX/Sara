# config.py

import os


def _env_int(name, default):

	value = os.getenv(name)

	if value is None:
		return default

	try:
		return int(value)
	except ValueError:
		return default


def _env_float(name, default):

	value = os.getenv(name)

	if value is None:
		return default

	try:
		return float(value)
	except ValueError:
		return default


def _env_bool(name, default=False):

	value = os.getenv(name)

	if value is None:
		return default

	return value.strip().lower() in {"1", "true", "yes", "on", "si", "s"}


FS = _env_int("FS", 16000)
CHUNK_MS = _env_int("CHUNK_MS", 100)
UMBRAL_VOZ = _env_int("UMBRAL_VOZ", 1100)
SILENCIO_MAXIMO = _env_float("SILENCIO_MAXIMO", 1.0)
MIN_HABLA_MS = _env_int("MIN_HABLA_MS", 350)

MODELO_WHISPER = os.getenv("MODELO_WHISPER", "base")
MODELO_IA = os.getenv("MODELO_IA", "gemma2:2b")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "auto")

ARCHIVO_AUDIO = os.getenv("ARCHIVO_AUDIO", "temp/grabacion.wav")
ARCHIVO_RESPUESTA = os.getenv("ARCHIVO_RESPUESTA", "temp/respuesta.mp3")

AVATAR_CERRADO = os.getenv("AVATAR_CERRADO", "assets/avatar/cerrado.png")
AVATAR_HABLANDO = os.getenv("AVATAR_HABLANDO", "assets/avatar/hablando.png")

SARA_TEXT_MODE = _env_bool("SARA_TEXT_MODE", False)
SARA_USAR_AVATAR = _env_bool("SARA_USAR_AVATAR", True)