def opensearch_existing_check(os_index, index_name, celex_list):
    """
    Checks for existing CELEX numbers in the specified OpenSearch index.

    This function iterates through the provided list of CELEX numbers and checks
    if each document already exists in the OpenSearch index identified by the given name.

    Args:
        connection (object): Connection object to the OpenSearch database.
        index_name (str): Name of the OpenSearch index to check for existing documents.
        celex_list (list): List of CELEX numbers to be checked.

    Returns:
        list: List containing CELEX numbers that are not present in the index.
    """
    non_existing = []
    for celex_id in celex_list:
        document_status = os_index.exists(index=index_name, id=celex_id)
        if document_status == False:
            non_existing.append(celex_id)

    return non_existing
