# Base Python légère
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=nfc_presence.settings \
    PYTHONPATH=/app

# Dépendances système pour pyscard/PCSC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pcscd pcsc-tools libpcsclite1 libpcsclite-dev \
    tzdata \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dépendances Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# Entrée
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
