from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_
import pandas as pd
from tasks.definitions import definition_extraction
from tasks.database.database_insert import insert_postgres
from tasks.database.database_update import update_postgres, update_processed_articles_records
import logging

def process_records_in_batches(database_engine):
    """
    Function to create the query to fetch all the articles and its metadata 
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    
    # Query must select the article records from the article table
    # where:
    #   1. celex document whose title is blank must not be considered
    #   2. celex_id must be after 2000
    #   3. article text must not be blank
    #   4. article text must comprises of Article followed by the Regulation or Directives or Decisions
    # Everything must be in ascending order of the primary key in article table

    metadata = MetaData()
    metadata.reflect(database_engine)

    articles_table = metadata.tables['articles']

    '''
    SELECT *
    FROM articles
    WHERE article_title = 'Scope' 
    AND article_text ~ '‘[^’]+’:[^.]+'
    AND article_text <> '';
    '''
    query = (
        articles_table.select()
        .select_from(
            articles_table
        )
        .where(
            and_(
                articles_table.c.article_title == 'Scope',
                articles_table.c.article_title != '',
                articles_table.c.article_text.op('~')('‘[^’]+’:[^.]+'),
            )
        )
    )

    # Fetch column headings separately
    column_headings = articles_table.columns.keys()

    with database_engine.connect().execution_options(stream_results=True) as conn:
        results = conn.execution_options(stream_results=True).execute(query)

        while True:
            results_chunk = results.fetchmany(100)
            if not results_chunk:
                break

            results_dict = [dict(zip(column_headings, row)) for row in results_chunk]
            success = False
            try:
                df_definitions = definition_extraction(results_dict)

                if not df_definitions.empty:
                    insert_postgres(database_engine, df_definitions, "definition_table")
                success = True
            except Exception as e:
                success = False
                logging.error(f'Error while inserting the dataframes in Postgresql due to error {e}')