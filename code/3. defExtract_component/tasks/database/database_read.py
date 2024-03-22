from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_, desc

def opensearch_query():
    """
    Constructs a query for OpenSearch to find documents that have not been processed.

    Returns:
        dict: A dictionary representing the OpenSearch query to find unprocessed documents.
    """
    # Construct the OpenSearch query dictionary
    record_query = {
                    "_source": "_id",
                    "query": {
                        "bool": {
                            "must_not": [
                                {
                                "nested": {
                                "path": "english.documentInformation",
                                "query": {
                                    "match_phrase": {
                                    "english.documentInformation.rawDocument": "no raw document present for the eurlex document"
                                    }
                                    }
                                }
                                },
                                {
                                "nested": {
                                "path": "english.documentInformation",
                                "query": {
                                    "match_phrase": {
                                    "english.documentInformation.documentContent": "Unfortunately this document cannot be displayed due to its size"
                                    }
                                    }
                                }
                                }
                            ],
                            "must": [
                                {
                                "nested": {
                                    "path": "english",
                                    "query": {
                                    "match_phrase": {
                                        "english.documentProcessedFlag": "N"
                                    }
                                    }
                                }
                                },
                                {
                                "nested": {
                                    "path": "english",
                                    "query": {
                                    "match_phrase": {
                                        "english.documentFormat": "HTML"
                                    }
                                    }
                                }
                                }
                            ]
                        }
                    }
                }

    return record_query


class PostgresReader():
    """
    A class for reading data from PostgreSQL tables related to documents and terms,
    specifically designed for the LexDrafter database schema.
    
    Attributes:
        engine (Engine): The SQLAlchemy engine connected to the PostgreSQL database.
        document_table (Table): The table containing document information.
        terms_table (Table): The table containing term definitions.
    """
    def __init__(self, pg_connection):
        """
        Initializes the PostgresReader instance by setting up the database connection
        and reflecting the database schema to access table definitions.

        Parameters:
            pg_connection (Engine): The SQLAlchemy engine for the PostgreSQL database connection.
        """
        self.engine = pg_connection

        metadata = MetaData()
        metadata.reflect(pg_connection)
    
        self.document_table = metadata.tables['lexdrafter_energy_document_information']
        self.terms_table = metadata.tables['lexdrafter_energy_definition_term']

    def get_document(self):
        """
        Retrieves documents from the database, including their IDs and CELEX IDs,
        and identifies the maximum document ID.

        Returns:
            tuple: A tuple containing the maximum document ID and a dictionary of documents.
        """
        # Query to select all documents
        doc_query = (self.document_table.select())

        with self.engine.connect().execution_options(stream_results=True) as conn:
            doc_results = conn.execution_options(stream_results=True).execute(doc_query)

            docs={}

            # Fetch documents in chunks to manage memory for large datasets
            while True:
                results_chunk = doc_results.fetchmany(20000)
                
                if not results_chunk:
                    break

                for row in results_chunk:
                    docs[row[1]]={"id": row[0], "celex_id": row[1]}

        # Query to find the maximum document ID
        doc_max_query = (
            self.document_table.select()
            .order_by(desc(self.document_table.c.id))
            .limit(1)
            .with_only_columns(self.document_table.c.id)
            )
        
        with self.engine.connect() as conn:
            max_results = conn.execute(doc_max_query)

            max_value = max_results.fetchone()

            if max_value:
                max_id = max_value[0]
            else:
                max_id = 0
        
        return max_id, docs
    

    def get_terms(self):
        """
        Retrieves terms from the database, including their IDs, associated document IDs,
        and the terms themselves, and identifies the maximum term ID.

        Returns:
            tuple: A tuple containing the maximum term ID and a dictionary of terms.
        """
        # Query to select all terms
        term_query = (self.terms_table.select())

        with self.engine.connect().execution_options(stream_results=True) as conn:
            term_results = conn.execution_options(stream_results=True).execute(term_query)

            term={}

            # Fetch terms in chunks to manage memory for large datasets
            while True:
                results_chunk = term_results.fetchmany(20000)
                if not results_chunk:
                    break

                for row in results_chunk:
                    term[row[2]]={"term_id": row[0], "doc_id": row[1], "term": row[2]}

        # Query to find the maximum term ID
        max_query = (
            self.terms_table.select()
            .order_by(desc(self.terms_table.c.term_id))
            .limit(1)
            .with_only_columns(self.terms_table.c.term_id)
            )
        
        with self.engine.connect() as conn:
            max_results = conn.execute(max_query)

            max_value = max_results.fetchone()

            if max_value:
                max_id = max_value[0]
            else:
                max_id = 0
        
        return max_id, term