FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias de sistema para audio, whisper y pygame.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    portaudio19-dev \
    libasound2 \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    tk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.docker.txt ./requirements.docker.txt
RUN pip install --upgrade pip && pip install -r requirements.docker.txt

COPY . .

CMD ["python", "main.py"]
