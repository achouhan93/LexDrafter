from tqdm import tqdm
from sqlalchemy import select, func, literal
import pandas as pd
import logging

def insert_postgres(database_engine, dataframe, table_name):
    """
    Insert the records from the dataframe into respective table in postgres

    Args:
        conn (database object): database connection object
        dataframe (dataframe): dataframe with the records present for each column
        table_name (string): table name present in the database
    """  
    # Use the JSONB data type for the columns containing JSON data
    dtype = {col_name: 'JSONB' for col_name in dataframe.columns if 'json' in str(dataframe[col_name].dtype)}
    
    # Insert data in batches using chunksize
    chunksize = 10000
    with database_engine.begin() as conn:
        for i in tqdm(range(0, len(dataframe), chunksize)):
            chunk = dataframe.iloc[i:i+chunksize]
            chunk.to_sql(name=table_name, con=conn, if_exists="append", schema="public", index=False, dtype=dtype, method='multi')  

def star_schema_postgres(connection, document_dataframes):
    """
    Function to insert the records in the star schema database
    """
    success = False

    try:
        # Title Information
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
