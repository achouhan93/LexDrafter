from tqdm import tqdm
from sqlalchemy import select, func, literal, MetaData
from sqlalchemy.dialects.postgresql import insert
import logging

class PostgresInsert():
    """
    A class for handling batch inserts into PostgreSQL tables, specifically designed
    for managing data related to energy documents, terms, explanations, relations, 
    and progress tracking in a LexDrafter database.

    Attributes:
        engine (Engine): The SQLAlchemy engine connected to the PostgreSQL database.
        batch_size (int): The size of each batch for bulk inserts to manage performance.
        document_table (Table): The table for energy document information.
        terms_table (Table): The table for energy definition terms.
        explanantion_table (Table): The table for explanations of energy terms.
        relation_table (Table): The table for relations between energy terms.
        progress_table (Table): The table for tracking progress of data insertion.
    """
    def __init__(self, pg_connection):
        """
        Initializes the PostgresInsert instance by setting up the database connection,
        reflecting the database schema to access table definitions, and initializing 
        the batch size for inserts.

        Parameters:
            pg_connection (Engine): The SQLAlchemy engine for the PostgreSQL database connection.
        """
        self.engine = pg_connection

        metadata = MetaData()
        metadata.reflect(pg_connection)
        self.batch_size = 10000
    
        self.document_table = metadata.tables['lexdrafter_energy_document_information']
        self.terms_table = metadata.tables['lexdrafter_energy_definition_term']
        self.explanantion_table = metadata.tables['lexdrafter_energy_term_explanation']
        self.relation_table = metadata.tables['lexdrafter_energy_term_relations']
        self.progress_table = metadata.tables['lexdrafter_energy_progress_table']


    # Function to insert nodes into the nodes table
    def insert_information(self, info, table_info):
        """
        Inserts a list of dictionaries (`info`) as records into a specified table in batches
        for efficient bulk insertion. The specific table is determined by the `table_info` parameter.

        Parameters:
            info (list of dict): The data to be inserted, where each dictionary represents a record.
            table_info (str): A string identifier to specify the target table. Valid values include 
                              "progress", "document", "term", "explanation", and "relation".

        Raises:
            ValueError: If `table_info` is not one of the expected identifiers.
        """
        if table_info == "progress":
            table = self.progress_table
        elif table_info == "document":
            table = self.document_table
        elif table_info == "term":
            table = self.terms_table
        elif table_info == "explanation":
            table = self.explanantion_table
        elif table_info == "relation":
            table = self.relation_table
        
        with self.engine.begin() as conn:
            for i in tqdm(range(0, len(info), self.batch_size)):
                batch = info[i: i + self.batch_size]
                insert_stmt = insert(table).values(batch)
                conn.execute(insert_stmt)