# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY alembic.ini ./
COPY alembic/ ./alembic/

COPY {{ cookiecutter.package_name }}/ ./{{ cookiecutter.package_name }}/

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash worker
RUN chown -R worker:worker /app
USER worker

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Команда по умолчанию
CMD ["poetry", "run", "faststream", "run", "{{ cookiecutter.package_name }}.handler:app", "--env", ".env", "--reload"]
