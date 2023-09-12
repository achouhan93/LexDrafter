from extractors.libraries import *
from extractors import *

CONST_EUTILS_DEFAULT_MINDATE = "1948"
CONST_EUTILS_DEFAULT_MAXDATE = datetime.date.today().strftime("%Y")

class Processor:
    def __init__(self, database_connection, index):
        self.connection = database_connection
        self.index_name = index


    def process_domain(self, domain_no, year, batchSize=100):
        if domain_no < 10:
            domain = '0' + str(domain_no)
        else:
            domain = str(domain_no)

        provided_url = 'https://eur-lex.europa.eu/search.html?name=browse-by%3Alegislation-in-force&type=named&displayProfile=allRelAllConsDocProfile&qid=1651004540876&CC_1_CODED=' + domain
        provided_url_year = provided_url + '&DD_YEAR=' + str(year)

        logging.info(f"URL for the respective year and domain: {provided_url_year}")

        # Calling the Function for the given CELEX_Numbers
        list_celex_number = celex_main(provided_url_year)
        non_existing_celex_number = opensearch_existing_check(self.connection, self.index_name, list_celex_number)

        logging.info(
            f"Considered {len(non_existing_celex_number)} new articles for year: {year} and domain: {domain_no}"
        )

        if len(non_existing_celex_number) == 0:
            progress_status = True
        else:
            progress_status = False

        for idBatch in tqdm(
            [non_existing_celex_number[i : i + batchSize] for i in range(0, len(non_existing_celex_number), batchSize)],
                desc=f"Inserting new article batches(size={len(non_existing_celex_number) if len(non_existing_celex_number) < batchSize else batchSize})",
        ):
            progress_status = get_document_information(self.connection, self.index_name, idBatch)

            if progress_status:
                continue
            else:
                return progress_status
        
        return progress_status


    def process_by_year(self, year):
        extraction_start_time = time()
        for domain_no in range(20, 0, -1):
            logging.info(f"Document extraction started for the year {year} and domain number {domain_no}")
            status = False

            status = self.process_domain(domain_no, year)

            if status:
                logging.info(f"Document extraction completed for the year {year} and domain number {domain_no} and took {secondsToText(time()-extraction_start_time)}")
            else:
                logging.info(f"Document extraction failed for the year {year} and domain number {domain_no}")


def insertDocumentsByTimeRange(database, index_name, mindate, maxdate):

    start_year = int(mindate)
    end_year = int(maxdate)

    document_processor = Processor(database, index_name)

    logging.info("**********************************")
    logging.info(f"Document extraction started for the year range: {start_year} to {end_year}")
    # Loop over the range of dates between start and end dates, with two days apart
    current_year = end_year
    while current_year >= start_year:
        year_start_time = time()
        logging.info(f"Document extraction started for the year {current_year}")
        document_processor.process_by_year(current_year)
        logging.info(f"Document extraction completed for the year {current_year} and took {secondsToText(time()- year_start_time)}")
        current_year -= 1
    
    logging.info(f"Document extraction finished for the year range: {start_year} to {end_year}")
    logging.info("**********************************")


def insertDocumentsByDomain(database_connection, database, domain_no, 
                            mindate, maxdate):
    
    start_year = int(mindate)
    end_year = int(maxdate)
    
    document_processor = Processor(database_connection, database)

    for domain in domain_no:
        logging.info("**********************************")
        logging.info(f"Document extraction started for the {domain_no} domain and year range: {start_year} to {end_year}")
        current_year = end_year
        while current_year >= start_year:
            year_start_time = time()

            logging.info(f"Document extraction started for the {domain} domain and year {current_year}")
            status = False

            status = document_processor.process_domain(int(domain), current_year)

            if status:
                logging.info(f"Document extraction completed for the {domain} domain and year {current_year} and took {secondsToText(time()-year_start_time)}")
            else:
                logging.info(f"Document extraction failed for the year {current_year} and domain number {domain}")

            current_year -= 1
    
    logging.info(f"Document extraction finished for the domain {domain_no} and year range: {start_year} to {end_year}")
    logging.info("**********************************")


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
    CONFIG = utils.loadConfigFromEnv()

    if not os.path.exists(CONFIG["LOG_PATH"]):
        os.makedirs(CONFIG["LOG_PATH"])
        print(f'created: {CONFIG["LOG_PATH"]} directory.')

    logging.basicConfig(
        filename=CONFIG["LOG_EXE_PATH"],
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
        level=logging.INFO,
    )

    start_time = time()
    logging.info(f"Current date and time: {secondsToText(start_time)}")
    database = CONFIG['DB_LEXDRAFTER_INDEX']

    database_connection = opensearch_connection()
    os_index_mapping = opensearch_en_mapping()
    opensearch_create(database_connection, database, os_index_mapping)

    parser = argparse.ArgumentParser("Specify the year duration for which eurlex documents are extracted")

    parser.add_argument(
        "--range",
        help="Start year of range yyyy and end year of range in yyyy",
        action="store_true"
    )  

    parser.add_argument(
        '--domain', 
        metavar="domain",
        type=str,
        nargs='+', 
        help='domain number(s) to insert records for')
    parser.add_argument('--minyear', default=CONST_EUTILS_DEFAULT_MINDATE, help='minimum year to insert records from')
    parser.add_argument('--maxyear', default=CONST_EUTILS_DEFAULT_MAXDATE, help='maximum year to insert records from') 

    args = parser.parse_args()

    if args.range:
        insertDocumentsByTimeRange(
            database_connection, database, args.minyear, args.maxyear
        )
        logging.info(f"Successfully Completed the extraction of the documents and it took {secondsToText(time() - start_time)}")
    
    elif args.domain:
        if len(args.domain) == 0:
            print("--domain expects atleast one argument: <domain no.>")
            sys.exit()
        elif (len(args.domain) > 0):
            insertDocumentsByDomain(
                database_connection, database, args.domain, args.minyear, args.maxyear
            )
    else:
        print("provide at least one argument.")
        sys.exit()


if __name__ == "__main__":
    main()