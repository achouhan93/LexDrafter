from sqlalchemy import Table, Column, MetaData, select, String
import re


def check_for_existing_records(connection, celex_information):
    """
    Checks for the existence of CELEX documents' logical structure in a PostgreSQL database.

    This function queries a PostgreSQL database to determine which CELEX documents, identified by their
    CELEX IDs in the provided list, already have their logical structure information stored. It filters out
    these documents from the input list.

    Args:
        connection (sqlalchemy.engine.base.Engine): A SQLAlchemy engine instance connected to the PostgreSQL database.
        celex_information (list of dict): A list of dictionaries, each containing the CELEX document information
                                          with a key '_id' representing the document's CELEX ID.

    Returns:
        list of dict: A filtered list of dictionaries, excluding those CELEX documents already present in the database.
    """
    metadata = MetaData()
    metadata.reflect(connection)

    table_name = metadata.tables["lexdrafter_energy_titles"]

    # Extract list of IDs from celex_information
    celex_ids = [info["_id"] for info in celex_information]

    # Construct and execute a query to find matching CELEX IDs in the database
    query = table_name.select().where(table_name.c.celex_id.in_(celex_ids))
    with connection.connect() as conn:
        result = conn.execute(query)

        # Create a set of existing CELEX IDs in the database
        existing_ids = set(row[0] for row in result)

    # Filter out documents whose IDs exist in the database
    celex_information = [
        info for info in celex_information if info["_id"] not in existing_ids
    ]

    return celex_information


def check_for_valid_documents_to_consider(celex_list):
    """
    Filters CELEX documents based on predefined criteria for validity.

    This function excludes documents based on their CELEX IDs, specifically those not starting with '3'
    or explicitly listed in a predefined exclusion list. It's designed to ensure that only valid and
    relevant documents are considered for further processing.

    Args:
        celex_list (list of dict): A list of dictionaries, each containing CELEX document information,
                                   with a key '_id' for the document's CELEX ID.

    Returns:
        list of dict: A filtered list of dictionaries, containing only the CELEX documents considered valid.
    """
    # Predefined list of CELEX IDs to exclude from consideration
    celex_not_consider = ["32012D0026", "32012D0398", "32019D1352"]

    # Identify invalid CELEX IDs either not starting with '3' or in the exclusion list
    celex_ids = [info["_id"] for info in celex_list]
    invalid_ids = set(
        celex
        for celex in celex_ids
        if ((re.search(r"^[3].*", celex) is None) or (celex in celex_not_consider))
    )

    # Filter out documents with invalid CELEX IDs
    valid_celex_list = [info for info in celex_list if info["_id"] not in invalid_ids]

    return valid_celex_list
