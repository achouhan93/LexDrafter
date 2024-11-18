from extractors.libraries import *


def opensearch_create(os_index, index_name, os_mapping):
    """
    Creates an OpenSearch index if it doesn't already exist.

    This function checks if an index with the provided name exists in the OpenSearch cluster.
    If the index is not found, it creates the index using the provided mapping.

    Args:
        os_index (object): An established connection object to the OpenSearch cluster.
        index_name (str): The desired name for the OpenSearch index.
        os_mapping (dict): A dictionary representing the mapping definition for the index.

    Returns:
        None
    """
    search_index = os_index.indices.exists(index=index_name)

    if search_index == False:
        os_index.indices.create(index=index_name, ignore=[400, 404], body=os_mapping)
