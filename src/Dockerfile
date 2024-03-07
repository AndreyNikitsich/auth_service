FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates openssl tzdata make git \
    gcc g++ openssh-client \
    llvm zip unzip wget \
    libxml2-dev libxml2-utils liblz4-dev libxslt-dev build-essential libpq-dev \
    libgeoip-dev libjpeg-dev liblzma-dev libncurses5-dev libncursesw5-dev \
    libffi-dev libssl-dev dnsutils liblzma-dev postgresql-client \
    libunwind-dev procps curl vis vim grep bash gettext \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"

COPY ./pyproject.toml ./poetry.lock* /app

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

RUN groupadd -r web && useradd -d /app -r -g web web_user \
    && chown web_user:web -R /app

USER web_user
ENTRYPOINT ["sh", "entrypoint.sh"]
