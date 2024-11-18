from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_, update
import pandas as pd
import logging
import json
from .citation_resolver import process_explanation
from tqdm import tqdm


def process_records_in_batches(database_engine, definition_table):
    """
    Processes records in batches from a specified table where the definition_type is 'dynamic'.
    For each record, it processes the explanation, updates the reference_list with the new information,
    and commits the changes to the database.

    This function iterates over each 'dynamic' record, utilizes a custom `process_explanation` function
    to generate new reference list data, and updates the record with this new data.

    Args:
        database_engine: The SQLAlchemy database engine instance used to connect to the database.
        definition_table: The SQLAlchemy table object representing the table to query and update.

    Returns:
        None. The function updates records in the database and does not return a value.
    """
    """
    SELECT
        term_id,
        explanation,
        reference_list,
        definition_type
    FROM lexdrafter_energy_definition_term
    WHERE definition_type = 'dynamic';
    """
    try:

        # Create a query to fetch records with a dynamic definition_type
        query = definition_table.select().where(
            definition_table.c.definition_type == "dynamic"
        )

        # Execute the query and process the results
        with database_engine.connect() as conn:
            results = conn.execute(query)
            for row in tqdm(results, desc="Processing records"):
                # Process the explanation for each record to generate new reference list data
                processed_info = process_explanation(row.explanation)
                # Serialize the processed information into a JSON string
                new_reference_list = json.dumps(processed_info)

                # Prepare an update query for the current record
                update_query = (
                    update(definition_table)
                    .where(
                        and_(
                            definition_table.c.term_id
                            == row.term_id,  # Match by term_id
                            definition_table.c.doc_id == row.doc_id,  # and doc_id
                        )
                    )
                    .values(reference_list=new_reference_list)
                )
                # Execute the update query
                conn.execute(update_query)

            # Commit the transaction to apply all changes made during the loop
            conn.commit()

        return True

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False
