from config import *
from logical_layout_extraction import layout_extraction
from tasks import *
from sqlalchemy import Table, MetaData
import utils
from time import time
import multiprocessing as mp


def celex_document_processing(celex, celex_document):
    celex_structural_information = {}

    logging.info(f"Extracting the logical structure of the document {celex}")
    document_html = celex_document['english']['documentInformation']['rawDocument']
    parsed_document = BeautifulSoup(document_html, 'html.parser')
    document = layout_extraction(parsed_document)
    title, recitals, chapter, section, articles, annex = document_fragment(celex, document)

    structural_information = {
        "title": title,
        "recitals": recitals,
        "chapter": chapter,
        "section": section,
        "articles": articles,
        "annex": annex
    }

    celex_structural_information[celex] = structural_information
    logging.info(f"Completed extraction of the structure of the {celex} document")

    return celex_structural_information


class Processor:
    def __init__(self, opensearch_connection, postgres_connection, index):
        self.os_connection = opensearch_connection
        self.pg_connection = postgres_connection
        self.index_name = index
        self.scroll_size = 100
        self.batch_size = 50
        
        # metadata = MetaData(bind=self.pg_connection)
        metadata = MetaData()
        metadata.reflect(self.pg_connection)
        self.articles_table = Table('lexdrafter_energy_articles', metadata, autoload=True)
        self.article_aux_table = Table('lexdrafter_energy_article_aux', metadata, autoload=True)
    

    def structure_extraction(self):
        try:
            search_params = opensearch_valid_record_query()

            # Execute the initial search request
            response = self.os_connection.search(
                index=self.index_name,
                scroll="50m",
                size=self.scroll_size,
                body=search_params
            )

            # Get the scroll ID and hits from the initial search request
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            total_docs = response["hits"]["total"]["value"]  # Get the total number of documents

            valid_document_count = 0

            with tqdm(total=total_docs) as pbar:
                while hits:
                    logging.info(
                        f"Considered {len(hits)} documents for processing"
                    )
                    document_count = len(hits)
                    hits = check_for_existing_records(self.pg_connection, hits)

                    logging.info(
                        f"{document_count - len(hits)} documents already exist. \n {len(hits)} new documents are considered for processing"
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

                        for idBatch in tqdm([hits[i : i + self.batch_size] for i in range(0, len(hits), self.batch_size)],
                            desc=f"Inserting structural information of batch (size={len(hits) if len(hits) < self.batch_size else self.batch_size})",
                            ):
                            results = [celex_document_processing(information['_id'], information['_source']) for information in tqdm(idBatch)]
                            batch_results.extend(results)
                        
                        status = star_schema_postgres(self.pg_connection, batch_results)

                        if status:
                            logging.info(f"Document structure information gathering completed for {len(hits)}")
                            update_opensearch_batch(self.os_connection, batch_results)
                        else:
                            logging.info(f"Document structure information gathering failed for {len(hits)}, refer logs")   

                    pbar.update(document_count)

                    # Paginate through the search results using the scroll parameter
                    response = self.os_connection.scroll(scroll_id=scroll_id, scroll="50m")
                    hits = response["hits"]["hits"]
                    scroll_id = response["_scroll_id"]
            
            logging.info(
                f"{valid_document_count} documents structural information is obtained from {total_docs} documents"
                )
            
            insert_article_aux(self.pg_connection, self.article_aux_table, self.articles_table) 
            progress_status = True       
        except Exception as e:
            progress_status = False
            logging.error(f'Error while extracting the structure due to error {e}')

        return progress_status


def secondsToText(secs):
    days = secs // 86400
    hours = (secs - days * 86400) // 3600
    minutes = (secs - days * 86400 - hours * 3600) // 60
    seconds = secs - days * 86400 - hours * 3600 - minutes * 60
    result = ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "") + \
             ("{0} hour{1}, ".format(hours, "s" if hours != 1 else "") if hours else "") + \
             ("{0} minute{1}, ".format(minutes, "s" if minutes != 1 else "") if minutes else "") + \
             ("{0} second{1}, ".format(round(seconds, 2), "s" if seconds != 1 else "") if seconds else "")
    return result


def main(argv=None):
    try:
        CONFIG = utils.loadConfigFromEnv()

        if not os.path.exists(CONFIG["LOG_PATH"]):
            os.makedirs(CONFIG["LOG_PATH"])
            print(f'created: {CONFIG["LOG_PATH"]} directory.')

        logging.basicConfig(
            filename=CONFIG["LOG_EXE_PATH"],
            filemode="a",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%y %H:%M:%S",
            level=logging.INFO
            )
        
        database = CONFIG['DB_LEXDRAFTER_INDEX']

        pg_connection = postgres_connection()
        os_connection = opensearch_connection()

        # parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-sc", "--schemacreation", help="extracting the logical structure of the document", action="store_true"
        )

        parser.add_argument(
            "-dc", "--datasetcreation", help="ground truth dataset creation for intext citation", action="store_true"
        )

        parser.add_argument(
            "-gt", "--groundtruthcreation", help="ground truth article text completion for intext citation", action="store_true"
        )

        parser.add_argument(
            "-an", "--analysis", help="analysis of the dataset", action="store_true"
        )

        args = parser.parse_args()

        document_processor = Processor(os_connection, pg_connection, database)

        if args.schemacreation:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the structure of the celex documents started")
            
            status = document_processor.structure_extraction()
            if status:
                logging.info(f"Completed the extraction of the structure of the celex documents and stored the information and took {secondsToText(time()- start_time)}")
            else:
                logging.info(f"Document extraction failed")
        
        if args.datasetcreation:
            start_time = time()
            logging.info(f"Ground truth dataset creation for intext citation started at {secondsToText(start_time)}")
            process_records_in_batches(pg_connection)
            logging.info(f"Ground truth dataset creation completed and took {secondsToText(time()- start_time)}")
        
        if args.groundtruthcreation:
            start_time = time()
            logging.info(f"Ground truth article text completion for intext citation started at {secondsToText(start_time)}")
            article_text_completion(pg_connection)
            logging.info(f"Ground truth article text completed successfully and took {secondsToText(time()- start_time)}")

        if args.analysis:
            logging.info("Analysis of the corpus")

            index_name="achouhan"
            
            counter = 0
            scroll_size = 200
            
            search_params = {
                                "query": {
                                    "nested": {
                                        "path": "english",
                                        "query": {
                                            "bool": {
                                                "must_not": {
                                                    "terms": {
                                                        "english.documentInformation.rawDocument": ["NA"]
                                                        },
                                                    "terms": {
                                                        "english.documentFormat": ["PDF", "NONE"]
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }

            # Execute the initial search request
            response = os_connection.search(
                index=index_name,
                scroll="5m",
                size=scroll_size,
                body=search_params
            )

            # Get the scroll ID and hits from the initial search request
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]
            total_docs = response["hits"]["total"]["value"]  # Get the total number of documents

            not_considered_count = 0
            not_considered_record = []

            considered_record = []
            html_considered_count = 0
            pdf_considered_count = 0
            none_considered_count = 0

            with tqdm(total=total_docs) as pbar:

                while hits:

                    for celex_documents in hits:
                        celex = celex_documents['_id']
                        documentFormat = celex_documents['_source']['english']['documentFormat']

                        if re.search(r'^[3].*', celex) is None: # Only Legal Acts Starting with 3 is considered
                            not_considered_count = not_considered_count + 1

                            not_considered_record.append(
                                {"celex_id": celex,
                                 "documentFormat": documentFormat}
                            )
                        else:
                            considered_record.append(
                                {"celex_id": celex,
                                 "documentFormat": documentFormat}
                            )

                            if documentFormat == "HTML":
                                html_considered_count = html_considered_count + 1
                            elif documentFormat == "PDF":
                                pdf_considered_count = pdf_considered_count + 1
                            elif documentFormat == "NONE":
                                none_considered_count = none_considered_count + 1
                        
                        pbar.update(1)

                    # Paginate through the search results using the scroll parameter
                    response = os_connection.scroll(scroll_id=scroll_id, scroll="5m")
                    hits = response["hits"]["hits"]
                    scroll_id = response["_scroll_id"]

            not_considered_dict = {
                "count": not_considered_count,
                "record": not_considered_record
            }

            considered_dict = {
                "count": html_considered_count+pdf_considered_count+none_considered_count,
                "html_count": html_considered_count,
                "pdf_count": pdf_considered_count,
                "none_count": none_considered_count,
                "records": considered_record
            }

            with open('./src/analysis/considered_documents.json', 'w') as f:
                json.dump(considered_dict, f)
            
            with open('./src/analysis/not_considered_documents.json', 'w') as f:
                json.dump(not_considered_dict, f)
    
    finally:
        pg_connection.dispose()


if __name__ == "__main__":
    main()