from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_, update
import pandas as pd
import logging
import json
from .citation_resolver import process_explanation
from tqdm import tqdm

def process_records_in_batches(database_engine, definition_table):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    '''
    SELECT
        term_id,
        explanation,
        reference_list,
        definition_type
    FROM lexdrafter_energy_definition_term
    WHERE definition_type = 'dynamic';
    '''
    query = (
        definition_table
        .select()
        .where(
            definition_table.c.definition_type == 'dynamic'
            )
    )

    with database_engine.connect() as conn:
        results = conn.execute(query)
        for row in tqdm(results):
            # Process each explanation
            processed_info = process_explanation(row.explanation)
            # Convert processed info to a JSON string (assuming reference_list expects JSON)
            new_reference_list = json.dumps(processed_info)
            
            # Update the record with the new reference_list
            update_query = (
                update(definition_table)
                .where(
                    and_(
                        definition_table.c.term_id == row.term_id,
                        definition_table.c.doc_id == row.doc_id
                        )
                )
                .values(reference_list=new_reference_list)
            )
            conn.execute(update_query)
        conn.commit()