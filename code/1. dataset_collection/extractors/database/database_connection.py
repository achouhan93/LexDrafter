import utils
from opensearchpy import OpenSearch

# Postgres and OpenSearch configuration details
CONFIG = utils.loadConfigFromEnv()

def opensearch_connection():
    """
    Establish the OpenSearch connection

    Returns:
        object: opensearch connection object
    """
    # OpenSearch Connection Setting
    user_name = CONFIG["DB_USERNAME"]
    password = CONFIG["DB_PASSWORD"]
    os = OpenSearch(hosts = [{'host': 'elastic-dbs.ifi.uni-heidelberg.de', 'port': 443}], 
    http_auth =(user_name, password), 
    use_ssl = True,
    verify_certs = True,
    ssl_assert_hostname = False,
    ssl_show_warn = False
    )

    return os