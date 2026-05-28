# config.py

import os


def _env_int(name, default):

	value = os.getenv(name)
	if value is None or value.strip() == "":
		return default
	try:
		return int(value)
	except ValueError:
		return default


def _env_float(name, default):

	value = os.getenv(name)
	if value is None or value.strip() == "":
		return default
	try:
		return float(value)
	except ValueError:
		return default


def _env_optional_int(name):

	value = os.getenv(name)
	if value is None or value.strip() == "":
		return None
	try:
		return int(value)
	except ValueError:
		return None


FS = _env_int("FS", 16000)
CHUNK_MS = _env_int("CHUNK_MS", 100)
UMBRAL_VOZ = _env_int("UMBRAL_VOZ", 1100)
SILENCIO_MAXIMO = _env_float("SILENCIO_MAXIMO", 1.0)
MIN_HABLA_MS = _env_int("MIN_HABLA_MS", 350)
INPUT_DEVICE = _env_optional_int("INPUT_DEVICE")

MODELO_WHISPER = "base"
MODELO_IA = "gemma2:2b"
WHISPER_DEVICE = "cuda"

ARCHIVO_AUDIO = "temp/grabacion.wav"
ARCHIVO_RESPUESTA = "temp/respuesta.mp3"

AVATAR_CERRADO = "assets/avatar/cerrado.png"
AVATAR_HABLANDO = "assets/avatar/hablando.png"

# Postgres settings (override with env vars if needed)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "escuela")
DB_USER = os.getenv("DB_USER", "jose")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")