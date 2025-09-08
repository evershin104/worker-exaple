import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Импортируем модели и настройки
from {{ cookiecutter.package_name }}.models import Base
from {{ cookiecutter.package_name }}.settings import DatabaseConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url() -> str:
    """
    Получает URL базы данных из настроек приложения
    
    Returns:
        str: URL подключения к базе данных
    """
    db_config = DatabaseConfig()
    return db_config.db_url


def run_migrations_offline() -> None:
    """
    Запуск миграций в 'offline' режиме.
    
    Настраивает контекст только с URL без создания Engine.
    Вызовы context.execute() выводят SQL в скрипт.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Выполняет миграции с переданным подключением
    
    Arguments:
        connection: Подключение к базе данных
    """
    context.configure(
        connection=connection, 
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Запуск миграций в асинхронном режиме
    """
    url = get_database_url()
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Запуск миграций в 'online' режиме.
    
    Создает асинхронный Engine и выполняет миграции.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()