from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_
import pandas as pd
import logging
import json


def process_records_in_batches(database_engine, data_split_table, term_table):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    '''
    SELECT
        ds.celex_id,
        ds.split,
        dt.term,
        ds.explanation
    FROM lexdrafter_energy_data_split ds
    JOIN lexdrafter_energy_definition_term dt ON ds.term_id = dt.term_id and ds.doc_id = dt.doc_id;
    '''
    query = (
        data_split_table
        .join(
            term_table,
            and_(
                data_split_table.c.term_id == term_table.c.term_id,
                data_split_table.c.doc_id == term_table.c.doc_id,
            )
        )
        .select()
        .where(
            and_(
                data_split_table.c.celex_id != None,
                data_split_table.c.split != None,
                term_table.c.term != None,
                data_split_table.c.explanation != None,
            )
        )
    )

    column_headings = ['celex_id', 'split', 'term_id', 'doc_id', 'explanation', 'term_id_1', 'doc_id_1', 'term', 'sentences']

    with database_engine.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(query)

        splits = {
            'train': [],
            'test': [],
            'validate': []
        }

        while True:
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_dict = [dict(zip(column_headings, row)) for row in results_chunk]
            
            for row in results_dict:
                split = row['split']
                original_definition = {
                    'term': row['term'],
                    'celex_id': row['celex_id'],
                    'original_definition': row['term'] + ' ' + row['explanation'],
                    'generated_definition': '',
                    'existing_sentences': row['sentences']
                }
                splits[split].append(original_definition)
            
            # Save each split to a JSON file
            for split, data in splits.items():
                with open(f'{split}_split.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4)


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
            # query = (
            #     select(data_split_table.c.celex_id)
            #     .where(
            #         term_table.c.term.ilike(f'%{term}%'),
            #         data_split_table.c.split_column == 'train'
            #     )
            # )
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