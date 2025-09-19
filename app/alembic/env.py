import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from database import Base, engine  # твой async_engine
import entities  # обязательно импортируй модели (Conversation, Message и др.)

# Alembic Config
config = context.config
fileConfig(config.config_file_name)

# Метаданные для автогенерации миграций
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск в offline-режиме (генерация SQL без коннекта)."""
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Запуск миграций в online-режиме."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Асинхронное подключение к БД для миграций."""
    connectable = engine
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

