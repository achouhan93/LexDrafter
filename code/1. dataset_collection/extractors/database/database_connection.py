import utils
from opensearchpy import OpenSearch

# Postgres and OpenSearch configuration details
CONFIG = utils.loadConfigFromEnv()

def opensearch_connection():
    """
    Establishes a secure connection to the OpenSearch database.

    This function retrieves connection details (host, port, username, password)
    from environment variables and creates an authenticated OpenSearch connection object.

    Returns:
        OpenSearch: An instance of the OpenSearch connection object.
    """
    # OpenSearch Connection Setting
    user_name = CONFIG["DB_USERNAME"]
    password = CONFIG["DB_PASSWORD"]
    os = OpenSearch(hosts = [{'host': CONFIG["DB_HOSTNAME"], 'port': CONFIG["DB_PORT"]}], 
        http_auth =(user_name, password), 
        use_ssl = True,
        verify_certs = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False
    )

    return os