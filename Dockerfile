# e-oficinas - imagem de produção (Coolify / VPS Hostinger)
# Settings: core.settings  |  WSGI: core.wsgi:application
# mysqlclient nao tem wheel manylinux -> compila com build-essential + libmysqlclient.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ON_DOCKER=1

WORKDIR /app

# Dependencias de sistema:
#  - build-essential/pkg-config/default-libmysqlclient-dev: compila o mysqlclient
#  - curl: usado pelo healthcheck do docker-compose
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Ponto de partida dos estaticos (WhiteNoise); o entrypoint roda de novo no boot
RUN chmod +x /app/docker/entrypoint.sh && \
    python manage.py collectstatic --noinput || true

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
