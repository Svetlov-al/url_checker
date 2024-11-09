# Stage 1: Builder
FROM python:3.11.5-slim-bullseye AS builder

# Копируем файлы для установки зависимостей
COPY poetry.lock pyproject.toml ./

# Устанавливаем Poetry и генерируем requirements файл
RUN python -m pip install poetry==1.8.2 && \
    poetry export --format requirements.txt --without-hashes -o requirements.txt

# Stage 2: Development
FROM python:3.11.5-slim-bullseye AS dev

# Переменные окружения
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Указываем рабочую директорию
WORKDIR /app

# Копируем зависимости из builder stage
COPY --from=builder requirements.txt ./

# Устанавливаем необходимые зависимости
RUN apt update -y && \
    apt install -y python3-dev gcc musl-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt remove --purge -y python3-dev gcc musl-dev && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Копируем всё содержимое проекта в рабочую директорию
COPY . .

# Указываем, какой порт будет открыт в контейнере
EXPOSE 8000