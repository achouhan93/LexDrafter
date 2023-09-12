from sqlalchemy import Table, Column, MetaData, select, String
import re

def check_for_existing_records(connection, celex_information):
    """
    Function to check if the logical structure of the celex ids
    are present in postgresql database

    Args:
        connection (object): postgresql connection object
        celex_information (list): list of dictionaries of all 
                                  the celex document information from opensearch

    Returns:
        list: list of dictionaries of all those celex documents whose structure is not in postgresql 
    """    
    metadata = MetaData()
    metadata.reflect(connection)

    table_name = metadata.tables['lexdrafter_energy_titles']

    # Extract list of IDs from celex_information
    celex_ids = [info['_id'] for info in celex_information]

    # Query for records with matching IDs
    query = (
        table_name.select()
        .where(table_name.c.celex_id.in_(celex_ids))
    )
    with connection.connect() as conn:
        result = conn.execute(query)

        # Create a set of IDs that exist in the database
        existing_ids = set(row[0] for row in result)

    # Remove any dictionaries with IDs that exist in the database
    celex_information = [info for info in celex_information if info['_id'] not in existing_ids]

    return celex_information


def check_for_valid_documents_to_consider(celex_list):
    celex_not_consider = ["32012D0026", "32012D0398", "32019D1352"]
    
    # Extract list of IDs from celex_information
    celex_ids = [info['_id'] for info in celex_list]

    invalid_ids = set(celex for celex in celex_ids if ((re.search(r'^[3].*', celex) is None) or (celex in celex_not_consider)))

    # Remove dictionaries with IDs that are invalid
    celex_list = [info for info in celex_list if info['_id'] not in invalid_ids]

    return celex_list 