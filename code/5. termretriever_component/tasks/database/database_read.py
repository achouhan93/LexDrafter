from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_
import pandas as pd
import logging
import json
from tqdm import tqdm


def process_records_in_batches(database_engine, term_table, definition_table, document_table):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    '''
    SELECT di.celex_id, dt.term, dt.sentences, te.explanation
    FROM lexdrafter_energy_term_explanation te
    JOIN lexdrafter_energy_definition_term dt ON dt.term_id = te.term_id and dt.doc_id = te.doc_id
    JOIN lexdrafter_energy_document_information di ON te.doc_id = di.id
    WHERE te.definition_type = 'static'
    '''
    query = (
        definition_table
        .join(
            term_table,
            and_(
                definition_table.c.term_id == term_table.c.term_id,
                definition_table.c.doc_id == term_table.c.doc_id,
            )
        )
        .join(
            document_table,
            document_table.c.id == term_table.c.doc_id
        )
        .select()
        .where(
            definition_table.c.definition_type == 'static'    
        )
    )

    records = []
    
    with database_engine.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(query)
        column_headings = results.keys()._keys

        while True:
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_dict = [dict(zip(column_headings, row)) for row in results_chunk]
            
            for row in tqdm(results_dict, desc="Processing records"):
                original_definition = {
                    'term': row['term'],
                    'celex_id': row['celex_id'],
                    'original_definition': f"'{row['term']}' {row['explanation']}",
                    'generated_definition': '',
                    'existing_sentences': row['sentences'],
                    'existing_record' : ["NEW TERM"]
                }
                records.append(original_definition)
            
    with open(f'./dataset/static_split.json', 'w') as json_file:
            json.dump(records, json_file, indent=4)


def fetch_existing_celex_ids(database_engine, data_split_table, term_table, terms):
    '''
    SELECT
        ds.celex_id,
        ds.split,
        dt.term,
        ds.explanation
    FROM lexdrafter_energy_data_split ds
    JOIN lexdrafter_energy_definition_term dt ON ds.term_id = dt.term_id and ds.doc_id = dt.doc_id;
    '''
    existing_records = {}

    with database_engine.connect() as conn:
        for term in terms:
            query = (
                select(data_split_table.c.celex_id)
                .where(
                    data_split_table.c.term_id.in_(
                        select(term_table.c.term_id)
                        .where(term_table.c.term == term)
                    ),
                    data_split_table.c.split == 'train'
                )
            )

            result = conn.execute(query)
            celex_ids = [row[0] for row in result.fetchall()]
            if celex_ids:
                existing_records[term] = celex_ids

    return existing_records


def extract_definition_corpus(database_engine, term_table, definition_table, document_table):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    '''
    SELECT di.celex_id, dt.term, te.explanation, te.reference_list
    FROM lexdrafter_energy_term_explanation te
    JOIN lexdrafter_energy_definition_term dt ON dt.term_id = te.term_id and dt.doc_id = te.doc_id
    JOIN lexdrafter_energy_document_information di ON te.doc_id = di.id
    '''
    query = (
        definition_table
        .join(
            term_table,
            and_(
                definition_table.c.term_id == term_table.c.term_id,
                definition_table.c.doc_id == term_table.c.doc_id,
            )
        )
        .join(
            document_table,
            document_table.c.id == term_table.c.doc_id
        )
        .select()
    )

    records = []
    
    with database_engine.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(query)
        column_headings = results.keys()._keys

        while True:
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_dict = [dict(zip(column_headings, row)) for row in results_chunk]
            
            for row in tqdm(results_dict, desc="Processing records"):
                original_definition = {
                    'celex_id': row['celex_id'],
                    'term': row['term'],
                    'term_definition': f"'{row['term']}' {row['explanation']}",
                    'reference_list' : row['reference_list']
                }
                records.append(original_definition)
            
    with open(f'./dataset/definition_corpus.json', 'w') as json_file:
            json.dump(records, json_file, indent=4)