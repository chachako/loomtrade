import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the project's root directory to the Python path
# This ensures that Alembic can find your application's modules,
# especially your models and database configuration.
# Assuming 'backend' is the root for alembic, and 'app' is inside 'backend'.
# Adjust if your alembic directory is elsewhere relative to your app.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your Base and all models here so Alembic can see them
from app.db.base_class import Base
# Import all models by importing the models package.
# The __init__.py in app/models/ should import all individual model classes.
import app.models # This will make all models accessible via Base.metadata

# Target metadata for 'autogenerate' support
# This should be your SQLAlchemy models' metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Return the database URL from an environment variable."""
    # Prefer DATABASE_URL from session.py as it might have fallbacks or load .env
    # However, directly using os.getenv is also common here.
    # Let's import the DATABASE_URL from our session configuration.
    try:
        from app.db.session import DATABASE_URL
        return DATABASE_URL
    except ImportError:
        # Fallback if session.py is not structured as expected or for some reason
        # DATABASE_URL is not directly importable.
        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            # A fallback, matching the one in session.py if it were not used
            db_url = "postgresql://vibetrade_user:vibetrade_password@db:5432/vibetrade_db"
            print(f"DATABASE_URL not found in environment or session.py, using default: {db_url}")
        return db_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
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

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the database URL
    db_url = get_url()

    # Create a new section in the config for the connectable attributes
    # This allows us to use engine_from_config with our dynamic URL
    connectable_config = config.get_section(config.config_ini_section)
    if connectable_config is None:
        connectable_config = {} # Initialize if section doesn't exist
    
    # Override sqlalchemy.url from alembic.ini with the one from our environment
    connectable_config["sqlalchemy.url"] = db_url
    
    connectable = engine_from_config(
        connectable_config, # Use the modified config section
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()