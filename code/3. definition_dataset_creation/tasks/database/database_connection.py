from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import utils


# Postgres and OpenSearch configuration details
CONFIG = utils.loadConfigFromEnv()


def postgres_connection():
    """
    Establish the postgresql connection

    Returns:
        object: postgresql connection object
    """
    # Postgresql Connection
    PG_USER = CONFIG['PG_USER']
    PG_PWD = CONFIG['PG_PWD']
    PG_DATABASE = CONFIG['PG_DATABASE']
    PG_SERVER = CONFIG['PG_SERVER']
    PG_HOST = CONFIG['PG_HOST']

    connection_string = f'postgresql://{PG_USER}:{PG_PWD}@{PG_SERVER}:{PG_HOST}/{PG_DATABASE}'
    connect_args = {'options': '-csearch_path=public'}
    database_engine = create_engine(connection_string, connect_args=connect_args, poolclass=QueuePool, pool_size=10, max_overflow=20)
    return database_engine