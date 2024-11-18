from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_
import pandas as pd
import logging
import json
from tqdm import tqdm
from database_connection import opensearch_connection
import utils

# Load configuration details from environment variables or other configuration sources
CONFIG = utils.loadConfigFromEnv()

opensearch_client = opensearch_connection()
LEXDRAFTER_INDEX = CONFIG["DB_LEXDRAFTER_INDEX"]


def process_records_in_batches(
    database_engine, term_table, definition_table, document_table
):
    """
    Function to create the query to fetch all the articles and its metadata
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    """
    SELECT di.celex_id, dt.term, dt.sentences, te.explanation
    FROM lexdrafter_energy_term_explanation te
    JOIN lexdrafter_energy_definition_term dt ON dt.term_id = te.term_id and dt.doc_id = te.doc_id
    JOIN lexdrafter_energy_document_information di ON te.doc_id = di.id
    WHERE te.definition_type = 'static'
    """
    query = (
        definition_table.join(
            term_table,
            and_(
                definition_table.c.term_id == term_table.c.term_id,
                definition_table.c.doc_id == term_table.c.doc_id,
            ),
        )
        .join(document_table, document_table.c.id == term_table.c.doc_id)
        .select()
        .where(definition_table.c.definition_type == "static")
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
                    "term": row["term"],
                    "celex_id": row["celex_id"],
                    "original_definition": f"'{row['term']}' {row['explanation']}",
                    "generated_definition": "",
                    "existing_sentences": row["sentences"],
                    "existing_record": ["NEW TERM"],
                }
                records.append(original_definition)

    with open(f"./dataset/static_split.json", "w") as json_file:
        json.dump(records, json_file, indent=4)


def extract_definition_corpus(
    database_engine, term_table, definition_table, document_table
):
    """
    Function to create the query to fetch all the articles and its metadata
    information

    Returns:
        string: postgresql query to fetch the article information
    """
    """
    SELECT di.celex_id, dt.term, te.explanation, te.reference_list
    FROM lexdrafter_energy_term_explanation te
    JOIN lexdrafter_energy_definition_term dt ON dt.term_id = te.term_id and dt.doc_id = te.doc_id
    JOIN lexdrafter_energy_document_information di ON te.doc_id = di.id
    """
    query = (
        definition_table.join(
            term_table,
            and_(
                definition_table.c.term_id == term_table.c.term_id,
                definition_table.c.doc_id == term_table.c.doc_id,
            ),
        )
        .join(document_table, document_table.c.id == term_table.c.doc_id)
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
                    "celex_id": row["celex_id"],
                    "term": row["term"],
                    "term_definition": f"'{row['term']}' {row['explanation']}",
                    "reference_list": row["reference_list"],
                }
                records.append(original_definition)

    with open(f"./dataset/definition_corpus.json", "w") as json_file:
        json.dump(records, json_file, indent=4)


# * Important: In Production, i.e., when actual drafting the document then changes are as follows:
# * Execute below function "process_records_in_batches_production" function from main instead
# * of "process_records_in_batches"
# !
# ! As the focus of the paper was to generate a definition and providing a reference
# ! to an existing definition is a simple look up to our definition-model. Therefore, this function
# ! was not called from the main.

# * For any queries, author can be contacted regarding the below function


# Only call this function when static and dynamic both definitions needs to be generated
def process_records_in_batches(
    database_engine,
    term_table,
    definition_table,
    document_table,
    data_split_table,
    eurovoc_descriptors,
):
    """
    Function to fetch all terms and their definitions from the table. For each term, check if its definition exists by
    calling `fetch_existing_celex_ids`. If not, perform the functionality for "NEW TERM".
    """
    # Query to fetch all terms and definitions without filtering by definition_type
    query = (
        definition_table.join(
            term_table,
            and_(
                definition_table.c.term_id == term_table.c.term_id,
                definition_table.c.doc_id == term_table.c.doc_id,
            ),
        )
        .join(document_table, document_table.c.id == term_table.c.doc_id)
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
                term = row["term"]
                celex_id = row["celex_id"]
                explanation = row["explanation"]

                # Check if the term definition exists
                existing_definitions = fetch_existing_celex_ids(
                    database_engine,
                    data_split_table,
                    term_table,
                    [term],  # Single term as a list
                    eurovoc_descriptors,
                )

                # If the term already has definitions, use the existing CELEX IDs
                if existing_definitions.get(term):
                    ranked_celex_ids = existing_definitions[term]
                    original_definition = {
                        "term": term,
                        "celex_id": celex_id,
                        "original_definition": f"'{term}' {explanation}",
                        "generated_definition": "",
                        "existing_sentences": row["sentences"],
                        "existing_record": ["EXISTING TERM"],
                        "ranked_celex_ids": ranked_celex_ids,
                    }
                else:
                    # Functionality for "NEW TERM"
                    original_definition = {
                        "term": term,
                        "celex_id": celex_id,
                        "original_definition": f"'{term}' {explanation}",
                        "generated_definition": "",
                        "existing_sentences": row["sentences"],
                        "existing_record": ["NEW TERM"],
                    }

                records.append(original_definition)

    # Save all records to a JSON file
    with open(f"./dataset/processed_terms.json", "w") as json_file:
        json.dump(records, json_file, indent=4)


def fetch_existing_celex_ids(
    database_engine, data_split_table, term_table, terms, eurovoc_descriptors
):
    """
    Fetch existing CELEX IDs for the given terms and rank them based on similarity of eurovoc_descriptors.

    Parameters:
        database_engine: SQLAlchemy database engine for querying the database.
        data_split_table: SQLAlchemy table object for the data split table.
        term_table: SQLAlchemy table object for the term table.
        terms: List of terms to search for.
        eurovoc_descriptors: List of eurovoc_descriptors to compare for similarity.

    Returns:
        A dictionary mapping terms to a list of ranked CELEX IDs based on eurovoc_descriptors similarity.
    """

    def get_eurovoc_descriptors_from_opensearch(celex_id):
        """
        Fetch eurovoc_descriptors for a given CELEX ID using OpenSearch.
        """
        response = opensearch_client.get(index=LEXDRAFTER_INDEX, id=celex_id)
        descriptors = response["_source"].get("eurovoc_descriptors", "")
        return [desc.strip() for desc in descriptors.split(",")]

    def calculate_similarity(desc1, desc2):
        """
        Calculate similarity between two lists of eurovoc_descriptors.
        Uses simple overlap ratio; can be replaced with advanced similarity measures.
        """
        set1, set2 = set(desc1), set(desc2)
        if not set1 or not set2:
            return 0
        return len(set1.intersection(set2)) / len(set1.union(set2))

    existing_records = {}

    with database_engine.connect() as conn:
        for term in terms:
            # Query to fetch CELEX IDs
            """
            SELECT
            ds.celex_id,
            ds.split,
            dt.term,
            ds.explanation
            FROM lexdrafter_energy_data_split ds
            JOIN lexdrafter_energy_definition_term dt ON ds.term_id = dt.term_id and ds.doc_id = dt.doc_id;
            """
            query = select(data_split_table.c.celex_id).where(
                data_split_table.c.term_id.in_(
                    select(term_table.c.term_id).where(term_table.c.term == term)
                ),
                data_split_table.c.split == "train",
            )

            result = conn.execute(query)
            celex_ids = [row[0] for row in result.fetchall()]

            if celex_ids:
                # Fetch eurovoc_descriptors for each CELEX ID from OpenSearch
                celex_descriptor_mapping = {}

                for celex_id in celex_ids:
                    descriptors = get_eurovoc_descriptors_from_opensearch(celex_id)
                    celex_descriptor_mapping[celex_id] = descriptors

                # Rank CELEX IDs by similarity of eurovoc_descriptors
                ranked_celex_ids = sorted(
                    celex_descriptor_mapping.keys(),
                    key=lambda cid: calculate_similarity(
                        eurovoc_descriptors, celex_descriptor_mapping[cid]
                    ),
                    reverse=True,
                )

                existing_records[term] = ranked_celex_ids

    return existing_records
