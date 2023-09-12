from sqlalchemy import MetaData

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
    if celex_information:
        metadata = MetaData()
        metadata.reflect(connection)

        table_name = metadata.tables['lexdrafter_energy_document_information']
        # celex_not_consider = ["32023R1066", "32020R0688", "32019R2035", "32016R0792"]
        # Reason for not considering
        # 32023R1066 => As the definition is not one per line but clubbed into numbers
        # 32020R0688 => Terms are defined with a filler term, i.e., ‘status free from “disease” ', now disease can be anything
        # 32019R2035 => Relation extraction issue
        # 32016R0792 => Duplicate sentence for different definition of 17th point

        celex_not_consider = ["32013R0617"]
        # 32013R0617 => Too complex definitions and repetative definitions

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
        celex_information = [info for info in celex_information if ((info['_id'] not in existing_ids) and (info['_id'] not in celex_not_consider))]

    return celex_information


def check_for_processed_records(connection, celex_information):
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

    table_name = metadata.tables['lexdrafter_energy_progress_table']

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
    celex_information = [info for info in celex_information if (info['_id'] not in existing_ids)]

    return celex_information