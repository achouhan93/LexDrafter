from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import utils
from opensearchpy import OpenSearch


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


def opensearch_connection():
    """
    Establish the OpenSearch connection

    Returns:
        object: opensearch connection object
    """
    # OpenSearch Connection Setting
    user_name = CONFIG["DB_USERNAME"]
    password = CONFIG["DB_PASSWORD"]
    os = OpenSearch(hosts = [{'host': CONFIG['DB_HOSTNAME'], 'port': CONFIG['DB_PORT']}], 
    http_auth =(user_name, password), 
    use_ssl = True,
    verify_certs = True,
    ssl_assert_hostname = False,
    ssl_show_warn = False
    )

    return os