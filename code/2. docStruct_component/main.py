# Import necessary modules and functions from external files and libraries
from config import *
from logical_layout_extraction import layout_extraction
from tasks import *
from sqlalchemy import Table, MetaData
import utils
from time import time
import multiprocessing as mp


def celex_document_processing(celex, celex_document):
    """
    Processes a single CELEX document to extract its structural information.

    Args:
        celex (str): The CELEX number of the document being processed.
        celex_document (dict): The document's content and metadata.

    Returns:
        dict: A dictionary containing the extracted structural information of the document.
    """

    # Initialize a dictionary to store the extracted structural information
    celex_structural_information = {}

    logging.info(f"Extracting the logical structure of the document {celex}")
    # Extract the raw HTML document from the provided document information
    document_html = celex_document["english"]["documentInformation"]["rawDocument"]

    # Parse the HTML document using BeautifulSoup
    parsed_document = BeautifulSoup(document_html, "html.parser")

    # Extract the logical layout of the parsed document
    document = layout_extraction(parsed_document)

    # Extract document fragments such as title, recitals, chapters, sections, articles, and annexes
    title, recitals, chapter, section, articles, annex = document_fragment(
        celex, document
    )

    # Compile the extracted information into a structured format
    structural_information = {
        "title": title,
        "recitals": recitals,
        "chapter": chapter,
        "section": section,
        "articles": articles,
        "annex": annex,
    }

    # Map the extracted structural information to the CELEX number of the document
    celex_structural_information[celex] = structural_information
    logging.info(f"Completed extraction of the structure of the {celex} document")

    # Return the extracted structural information
    return celex_structural_information


class Processor:
    """
    Processor class responsible for processing documents from an OpenSearch database, extracting their structural information,
    and storing this information into a PostgreSQL database.
    """

    def __init__(self, opensearch_connection, postgres_connection, index):
        """
        Initializes the Processor object with connections to databases and the index to process documents from.

        Args:
            opensearch_connection (object): Connection object to OpenSearch database.
            postgres_connection (object): Connection object to Postgres database.
            index (str): Name of the OpenSearch index to process documents from.
        """

        self.os_connection = opensearch_connection
        self.pg_connection = postgres_connection
        self.index_name = index
        self.scroll_size = 100
        self.batch_size = 50

        # Reflect the structure of existing tables in the PostgreSQL database into SQLAlchemy metadata object
        metadata = MetaData()
        metadata.reflect(self.pg_connection)
        self.articles_table = Table(
            "lexdrafter_energy_articles", metadata, autoload=True
        )
        self.article_aux_table = Table(
            "lexdrafter_energy_article_aux", metadata, autoload=True
        )

    def structure_extraction(self):
        """
        This method extracts the logical structure of documents from OpenSearch and stores the information in the Postgres database.

        Returns:
            bool: True if the extraction process was successful, False otherwise.
        """
        try:
            # Define the search parameters for finding valid records in OpenSearch
            search_params = opensearch_valid_record_query()

            # Execute the initial search request
            response = self.os_connection.search(
                index=self.index_name,
                scroll="50m",
                size=self.scroll_size,
                body=search_params,
            )

            # Get the scroll ID and hits from the initial search request
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            total_docs = response["hits"]["total"][
                "value"
            ]  # Get the total number of documents

            valid_document_count = 0

            with tqdm(total=total_docs) as pbar:
                while hits:
                    logging.info(f"Considered {len(hits)} documents for processing")
                    document_count = len(hits)
                    hits = check_for_existing_records(self.pg_connection, hits)

                    logging.info(
                        f"{document_count - len(hits)} documents does not exist. \n {len(hits)} new documents are considered for processing"
                    )

                    non_existing_count = len(hits)

                    hits = check_for_valid_documents_to_consider(hits)
                    valid_document_count = valid_document_count + len(hits)

                    logging.info(
                        f"{non_existing_count - len(hits)} documents are valid documents. \n {len(hits)} valid new documents are considered for processing"
                    )

                    if len(hits) == 0:
                        progress_status = True
                    else:
                        progress_status = False

                    if not progress_status:
                        batch_results = []

                        for idBatch in tqdm(
                            [
                                hits[i : i + self.batch_size]
                                for i in range(0, len(hits), self.batch_size)
                            ],
                            desc=f"Inserting structural information of batch (size={len(hits) if len(hits) < self.batch_size else self.batch_size})",
                        ):
                            results = [
                                celex_document_processing(
                                    information["_id"], information["_source"]
                                )
                                for information in tqdm(idBatch)
                            ]
                            batch_results.extend(results)

                        status = star_schema_postgres(self.pg_connection, batch_results)

                        if status:
                            logging.info(
                                f"Document structure information gathering completed for {len(hits)}"
                            )
                            update_opensearch_batch(self.os_connection, batch_results)
                        else:
                            logging.info(
                                f"Document structure information gathering failed for {len(hits)}, refer logs"
                            )

                    pbar.update(document_count)

                    # Paginate through the search results using the scroll parameter
                    response = self.os_connection.scroll(
                        scroll_id=scroll_id, scroll="50m"
                    )
                    hits = response["hits"]["hits"]
                    scroll_id = response["_scroll_id"]

            logging.info(
                f"{valid_document_count} documents structural information is obtained from {total_docs} documents"
            )

            insert_article_aux(
                self.pg_connection, self.article_aux_table, self.articles_table
            )
            progress_status = True
        except Exception as e:
            progress_status = False
            logging.error(f"Error while extracting the structure due to error {e}")

        return progress_status


def secondsToText(secs):
    """
    Converts a duration from seconds into a human-readable string format.

    Args:
        secs (int): The duration in seconds to convert.

    Returns:
        str: A human-readable string representation of the duration, breaking it down into days, hours, minutes, and seconds.
    """
    days = secs // 86400
    hours = (secs - days * 86400) // 3600
    minutes = (secs - days * 86400 - hours * 3600) // 60
    seconds = secs - days * 86400 - hours * 3600 - minutes * 60
    result = (
        ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "")
        + ("{0} hour{1}, ".format(hours, "s" if hours != 1 else "") if hours else "")
        + (
            "{0} minute{1}, ".format(minutes, "s" if minutes != 1 else "")
            if minutes
            else ""
        )
        + (
            "{0} second{1}, ".format(round(seconds, 2), "s" if seconds != 1 else "")
            if seconds
            else ""
        )
    )
    return result


def main(argv=None):
    """
    Main function to orchestrate the document processing flow.

    This function sets up the environment by loading configuration, initializing loggings, connecting to databases,
    and then, based on command line arguments, initiates the process to extract the logical structure of documents.

    Args:
        argv (list, optional): A list of command line arguments. Defaults to None.
    """
    try:
        # Load configuration from environment variables
        CONFIG = utils.loadConfigFromEnv()

        # Create log directory if it doesn't exist
        if not os.path.exists(CONFIG["LOG_PATH"]):
            os.makedirs(CONFIG["LOG_PATH"])
            print(f'created: {CONFIG["LOG_PATH"]} directory.')

        # Set up logging configuration
        logging.basicConfig(
            filename=CONFIG["LOG_EXE_PATH"],
            filemode="a",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%y %H:%M:%S",
            level=logging.INFO,
        )

        # Establish connections to databases
        database = CONFIG["DB_LEXDRAFTER_INDEX"]
        pg_connection = postgres_connection()
        os_connection = opensearch_connection()

        # Parse command line arguments for additional operations
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-sc",
            "--schemacreation",
            help="extracting the logical structure of the document",
            action="store_true",
        )

        args = parser.parse_args()

        # Initialize document processor with database connections and start processing
        document_processor = Processor(os_connection, pg_connection, database)

        if args.schemacreation:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(
                f"Process to extracting the structure of the celex documents started"
            )

            status = document_processor.structure_extraction()
            if status:
                logging.info(
                    f"Completed the extraction of the structure of the celex documents and stored the information and took {secondsToText(time()- start_time)}"
                )
            else:
                logging.info(f"Document extraction failed")

    finally:
        # Ensure that the PostgreSQL connection is properly disposed
        pg_connection.dispose()


if __name__ == "__main__":
    main()
