import os
from logging.config import fileConfig

from alembic import context
from app.database.settings.base import Base
from dotenv import load_dotenv
from sqlalchemy import (
    engine_from_config,
    pool,
)


load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URI", "").replace("+asyncpg", "")

from app.adapters.orm.abusive_experience import AbusiveExperienceModel  # noqa
from app.adapters.orm.base_link import LinkModel  # noqa
from app.adapters.orm.virus_total import VirusTotalModel  # noqa


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well.  By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script
    output.

    """
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = SQLALCHEMY_DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()