from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import utils
from opensearchpy import OpenSearch


# Load configuration details from environment variables or other configuration sources
CONFIG = utils.loadConfigFromEnv()


def postgres_connection():
    """
    Establishes a connection to a PostgreSQL database using configurations loaded from the environment.

    The function creates a SQLAlchemy engine instance configured for a PostgreSQL database. It utilizes
    connection pooling to manage database connections efficiently.

    Returns:
        sqlalchemy.engine.base.Engine: A SQLAlchemy engine instance connected to the PostgreSQL database.
    """
    # Configuration parameters extracted from CONFIG
    PG_USER = CONFIG["PG_USER"]
    PG_PWD = CONFIG["PG_PWD"]
    PG_DATABASE = CONFIG["PG_DATABASE"]
    PG_SERVER = CONFIG["PG_SERVER"]
    PG_HOST = CONFIG["PG_HOST"]

    # Connection string formatted using PostgreSQL connection parameters
    connection_string = (
        f"postgresql://{PG_USER}:{PG_PWD}@{PG_SERVER}:{PG_HOST}/{PG_DATABASE}"
    )

    # Additional connection arguments, e.g., setting the search path to the public schema
    connect_args = {"options": "-csearch_path=public"}

    # Creation of the SQLAlchemy engine with a QueuePool for connection pooling
    database_engine = create_engine(
        connection_string,
        connect_args=connect_args,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
    )

    return database_engine
