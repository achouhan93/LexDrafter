from .database.database_connection import postgres_connection as postgres_connection
from .database.database_read import (
    process_records_in_batches as process_records_in_batches,
    fetch_existing_celex_ids as fetch_existing_celex_ids,
    extract_definition_corpus as extract_definition_corpus,
)
from .statement_processing import calculate_sentence_score as calculate_sentence_score
