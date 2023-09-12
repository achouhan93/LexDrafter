from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_, desc

def opensearch_valid_record_query():
    valid_record_query = {
                    "_source": "english.documentInformation.rawDocument",
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
                                        "english.structureProcessedFlag": "N"
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
    
    return valid_record_query

def opensearch_query():
    record_query = {
                    "_source": "_id",
                      "sort": [
                        {
                        "_id": {
                            "order": "desc"
                        }
                        }
                    ],
                    "query": {
                        "nested": {
                        "path": "english",
                        "query": {
                            "term": {
                            "english.documentProcessedFlag": {
                                "value": "N"
                            }
                            }
                        }
                        }
                    }
                }

    return record_query


class PostgresReader():

    def __init__(self, pg_connection):
        self.engine = pg_connection

        metadata = MetaData()
        metadata.reflect(pg_connection)
    
        self.document_table = metadata.tables['lexdrafter_energy_document_information']
        self.terms_table = metadata.tables['lexdrafter_energy_definition_term']

    def get_document(self):
        doc_query = (self.document_table.select())

        with self.engine.connect().execution_options(stream_results=True) as conn:
            doc_results = conn.execution_options(stream_results=True).execute(doc_query)

            docs={}

            while True:
                results_chunk = doc_results.fetchmany(20000)
                
                if not results_chunk:
                    break

                for row in results_chunk:
                    docs[row[1]]={"id": row[0], "celex_id": row[1]}

        # Get the max id
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
        term_query = (self.terms_table.select())

        with self.engine.connect().execution_options(stream_results=True) as conn:
            term_results = conn.execution_options(stream_results=True).execute(term_query)

            term={}

            while True:
                results_chunk = term_results.fetchmany(20000)
                if not results_chunk:
                    break

                for row in results_chunk:
                    term[row[2]]={"term_id": row[0], "doc_id": row[1], "term": row[2]}

        # Get the max id
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