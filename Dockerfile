# Stage 1: Builder
FROM python:3.12.1-slim-bullseye AS builder

# => Копируем файлы для установки зависимостей
COPY poetry.lock pyproject.toml ./

# => Устанавливаем Poetry и генерируем requirements файлы
RUN python -m pip install poetry==1.8.2 && \
    poetry export --with=lint -o requirements.lint.txt --without-hashes

# Stage 2: Development
FROM python:3.12.1-slim-bullseye AS dev

WORKDIR /app

# => Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# => Копируем зависимости из builder stage
COPY --from=builder requirements.lint.txt /app

# => Устанавливаем необходимые зависимости для разработки
RUN apt update -y && \
    apt install -y python3-dev gcc musl-dev && \
    pip install --upgrade pip && pip install --no-cache-dir -r requirements.lint.txt

# => Копируем код приложения
COPY /app/ /app/

# => Копируем конфигурацию Alembic
COPY alembic.ini /

# => Указываем порт, который будет открыт в контейнере
EXPOSE 8000
