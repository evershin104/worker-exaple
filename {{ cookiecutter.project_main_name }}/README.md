# Worker Example

Асинхронное приложение для обработки задач из очереди RabbitMQ с логированием в PostgreSQL.

## Быстрый запуск

### С Docker Compose

```bash
# Копируем пример переменных окружения
cp env.example .env

# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f {{ cookiecutter.package_name }}

# Остановка
docker-compose down
```

### Локальная разработка

```bash
# Установка зависимостей
poetry install

# Применение миграций (если нужно)
poetry run alembic upgrade head

# Запуск воркера
poetry run faststream run {{ cookiecutter.package_name }}.handler:app --reload --env .env
```

## Сервисы

- **Worker** - основное приложение (порт не нужен)
- **PostgreSQL** - база данных (порт 5432)
- **RabbitMQ** - брокер сообщений (порт 5672)
- **RabbitMQ Management** - веб-интерфейс (порт 15672)

## Переменные окружения

### Для Docker Compose

Создайте файл `.env` на основе `env.example`:

```bash
# PostgreSQL
POSTGRES_DB={{ cookiecutter.package_name }}
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
```

### Для локальной разработки

Создайте файл `.env` с теми же переменными, но с `localhost` для хостов.

## Архитектура

- **FastStream** - фреймворк для работы с очередями
- **SQLAlchemy 2.0** - ORM для работы с БД
- **PostgreSQL** - база данных
- **RabbitMQ** - брокер сообщений
