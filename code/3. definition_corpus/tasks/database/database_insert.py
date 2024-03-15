from tqdm import tqdm
from sqlalchemy import select, func, literal, MetaData
from sqlalchemy.dialects.postgresql import insert
import logging

class PostgresInsert():

    def __init__(self, pg_connection):
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