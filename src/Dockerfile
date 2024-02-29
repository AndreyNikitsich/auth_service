FROM python:3.11-slim-buster as requirements-stage

WORKDIR /tmp

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.7.1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim-buster

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

RUN groupadd -r web && useradd -d /app -r -g web web_user \
    && chown web_user:web -R /app

USER web_user
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
