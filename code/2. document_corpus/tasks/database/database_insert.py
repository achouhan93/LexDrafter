from tqdm import tqdm
from sqlalchemy import select, func, literal
import pandas as pd
import logging

def insert_postgres(database_engine, dataframe, table_name):
    """
    Inserts records from a Pandas DataFrame into a PostgreSQL table.

    This function takes a DataFrame and inserts its contents into a specified PostgreSQL table.
    It utilizes a chunked approach for large DataFrames to manage memory and performance. It is also
    capable of handling JSONB data types for columns containing JSON data.

    Args:
        database_engine (sqlalchemy.engine.base.Engine): A SQLAlchemy engine instance connected to the PostgreSQL database.
        dataframe (pandas.DataFrame): The DataFrame containing the records to be inserted.
        table_name (str): The name of the target table in the PostgreSQL database.
    """  
    # Identify columns with JSON data for JSONB data type specification
    dtype = {col_name: 'JSONB' for col_name in dataframe.columns if 'json' in str(dataframe[col_name].dtype)}
    
    # Define chunk size for batch insertions
    chunksize = 10000
    with database_engine.begin() as conn:
        for i in tqdm(range(0, len(dataframe), chunksize)):
            chunk = dataframe.iloc[i:i+chunksize]
            chunk.to_sql(name=table_name, con=conn, if_exists="append", schema="public", index=False, dtype=dtype, method='multi')  

def star_schema_postgres(connection, document_dataframes):
    """
    Inserts records into a PostgreSQL database according to a star schema structure from document dataframes.

    This function iteratively inserts data from multiple DataFrames related to various aspects of documents
    (titles, recitals, chapters, sections, articles, annexes) into corresponding PostgreSQL tables.

    Args:
        connection (sqlalchemy.engine.base.Engine): A SQLAlchemy engine instance for the PostgreSQL database.
        document_dataframes (list): A list of dictionaries containing DataFrames for different parts of documents.

    Returns:
        bool: True if all inserts were successful, False if an error occurred.
    """
    success = False

    try:
        # Process and insert DataFrames for each document part
        title_df = pd.concat([list(value.values())[0]['title'] for value in document_dataframes])
        
        if len(title_df.index) != 0:
            insert_postgres(connection, title_df, "lexdrafter_energy_titles")

        # Recitals Information
        recitals_df = pd.concat([list(value.values())[0]['recitals'] for value in document_dataframes])

        if len(recitals_df.index) != 0:
            insert_postgres(connection, recitals_df, "lexdrafter_energy_recitals")

        # Chapter Information
        chapter_df = pd.concat([list(value.values())[0]['chapter'] for value in document_dataframes])

        if len(chapter_df.index) != 0:    
            insert_postgres(connection, chapter_df, "lexdrafter_energy_chapters")

        # Section Information
        section_df = pd.concat([list(value.values())[0]['section'] for value in document_dataframes])
        
        if len(section_df.index) != 0: 
            insert_postgres(connection, section_df, "lexdrafter_energy_sections")

        # Article Information
        articles_df = pd.concat([list(value.values())[0]['articles'] for value in document_dataframes])
        
        if len(articles_df.index) != 0: 
            insert_postgres(connection, articles_df, "lexdrafter_energy_articles")

        # Annex Information
        annex_df = pd.concat([list(value.values())[0]['annex'] for value in document_dataframes])
        
        if len(annex_df.index) != 0: 
            insert_postgres(connection, annex_df, "lexdrafter_energy_annexs")

        success = True
        return success
    
    except Exception as e:
        success = False
        logging.error(f'Error while inserting the dataframes in Postgresql due to error {e}')
        return success


def insert_article_aux(connection, article_aux_table, articles_table):
    """
    Populates an auxiliary table with article information from an articles table.

    Constructs and executes a SQL query to insert article metadata into an auxiliary table,
    creating a unique identifier for each article based on multiple fields.

    Args:
        connection (sqlalchemy.engine.base.Engine): A SQLAlchemy engine instance for the PostgreSQL database.
        article_aux_table (sqlalchemy.Table): SQLAlchemy table object for the auxiliary table.
        articles_table (sqlalchemy.Table): SQLAlchemy table object for the articles table.
    """
    insert_query = (
        article_aux_table.insert()
        .from_select(
            ['article_info', 'flag'],
            select([
                func.concat(
                    articles_table.c.celex_id,
                    '-', articles_table.c.chapter_number,
                    '-', articles_table.c.section_number,
                    '-', articles_table.c.article_number,
                    '-', articles_table.c.article_fragment_number
                ),
                literal('N')
            ])
            .select_from(articles_table)
        )
        .on_conflict_do_nothing()
    )

    with connection.connect() as conn:
        conn.execute(insert_query)
