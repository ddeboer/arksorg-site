
import functools
import logging
import os
import os.path
import typing

import pydantic_settings

ENV_PREFIX = "arks_"
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE_KEY = f"{ENV_PREFIX.upper()}SETTINGS"


class Settings(pydantic_settings.BaseSettings):
    # env_prefix provides the environment variable prefix
    # for overriding these settings with env vars.
    # e.g. ARKS_PORT=11000
    model_config = pydantic_settings.SettingsConfigDict(env_prefix=ENV_PREFIX, env_file=".env")
    # Host for the development server
    devhost: str = "localhost"
    # Port for the development server
    devport: int = 8000
    # An sqlalchemy database connection string for the registry configuration
    db_connection_string: str = f"sqlite:///{BASE_FOLDER}/data/registry.sqlite"
    # Label for the type of environment we are running under, e.g. "development", "production"
    environment: str = "production"
    # Allow application information to be exposed in the api
    allow_appinfo: bool = False
    # Path to logfile, fall back to stderr if None
    log_filename: typing.Optional[str] = None
    log_level: str = "info"
    log_format: str = logging.BASIC_FORMAT
    # Log sql queries
    debug_sql: bool = False
    # Folder containing static content specific to this application.
    static_dir: str = os.path.join(BASE_FOLDER, "static")
    # Templates used by this application
    template_dir: str = os.path.join(BASE_FOLDER, "templates")
    # The public naan and shoulder source URL
    naans_source: str = "https://cdluc3.github.io/naan_reg_public/naan_records.json"


@functools.lru_cache
def get_settings(env_file=None):
    if env_file is None:
        env_file = os.environ.get(SETTINGS_FILE_KEY, ".env")
    return Settings(_env_file=env_file)
