from sqlalchemy import MetaData


def check_for_existing_records(connection, celex_information):
    """
    Checks for the presence of documents in the PostgreSQL database based on CELEX IDs provided in
    `celex_information`. This function identifies documents whose structures are not already present in the database.

    Args:
        connection (object): The PostgreSQL connection object.
        celex_information (list): A list of dictionaries containing document information from OpenSearch,
                                  with each dictionary expected to have a '_id' key representing the CELEX ID.

    Returns:
        list: A list of dictionaries for documents not present in the PostgreSQL database,
              filtering out documents based on predefined exclusion criteria.
    """
    if celex_information:
        metadata = MetaData()
        metadata.reflect(connection)

        table_name = metadata.tables["lexdrafter_energy_document_information"]

        # Predefined list of CELEX IDs to exclude from consideration
        # celex_not_consider = []
        celex_not_consider = ["32013R0617"]
        # Reason for not considering
        # 32013R0617 => Too complex definitions and repetative definitions

        # Extract list of IDs from celex_information
        celex_ids = [info["_id"] for info in celex_information]

        # Perform a query to find records with matching CELEX IDs
        query = table_name.select().where(table_name.c.celex_id.in_(celex_ids))
        with connection.connect() as conn:
            result = conn.execute(query)

            # Create a set of IDs that exist in the database
            existing_ids = set(row[0] for row in result)

        # Filter out documents that either exist in the database or are in the exclusion list
        celex_information = [
            info
            for info in celex_information
            if (
                (info["_id"] not in existing_ids)
                and (info["_id"] not in celex_not_consider)
            )
        ]

    return celex_information


def check_for_processed_records(connection, celex_information):
    """
    Checks if the logical structures of the CELEX IDs provided in `celex_information`
    are marked as processed in the PostgreSQL database.

    This function is specifically for identifying documents that have not been marked
    as processed in a specific progress-tracking table.

    Args:
        connection (object): The PostgreSQL connection object.
        celex_information (list): A list of dictionaries of document information from OpenSearch,
                                  each expected to contain a '_id' key for the CELEX ID.

    Returns:
        list: A list of dictionaries for documents whose CELEX IDs are not found in the
              progress-tracking table, indicating they have not been processed.
    """
    metadata = MetaData()
    metadata.reflect(connection)

    table_name = metadata.tables["lexdrafter_energy_progress_table"]

    # Extract list of IDs from celex_information
    celex_ids = [info["_id"] for info in celex_information]

    # Query for records with matching CELEX IDs in the progress-tracking table
    query = table_name.select().where(table_name.c.celex_id.in_(celex_ids))
    with connection.connect() as conn:
        result = conn.execute(query)

        # Create a set of IDs that exist in the database
        existing_ids = set(row[0] for row in result)

    # Filter out documents marked as processed (existing in the progress table)
    celex_information = [
        info for info in celex_information if (info["_id"] not in existing_ids)
    ]

    return celex_information
