from config import *
from tasks import *
from sqlalchemy import Table, MetaData
import utils
from time import time
import multiprocessing as mp


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
        
        pg_connection = postgres_connection()
        
        metadata = MetaData()
        metadata.reflect(pg_connection)
        
        term_table = metadata.tables['lexdrafter_energy_definition_term']
        definition_table = metadata.tables['lexdrafter_energy_term_explanation']
        document_table = metadata.tables['lexdrafter_energy_document_information']

        # parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-st", "--staticdefinitiondataset", help="Extracting the static definitions", action = "store_true" 
        )

        parser.add_argument(
            "-s", "--evaluationdatasetscoring", help="Assign score to each sentence where term is present", action = "store_true" 
        )

        parser.add_argument(
            "-dc", "--definitioncorpus", help="Extracting the definition corpus", action = "store_true" 
        )

        args = parser.parse_args()

        if args.staticdefinitiondataset:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the defnition of terms present in the celex documents started")
            
            status = process_records_in_batches(pg_connection, term_table, definition_table, document_table)
            
            if status:
                logging.info(f"Completed the extraction of the structure of the celex documents and stored the information and took {secondsToText(time()- start_time)}")
            else:
                logging.info(f"Document extraction failed")

        if args.evaluationdatasetscoring:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to assigning score to the statements where term exist")
            
            file_name = f'./dataset/static_split.json'
            
            # Read JSON file
            with open(file_name, 'r') as json_file:
                updated_data = json.load(json_file)

            score_data = calculate_sentence_score(updated_data)

            # Save the updated JSON data with scores
            with open(f'./dataset/static_split_score.json', 'w') as json_file:
                json.dump(score_data, json_file, indent=4) 

        if args.definitioncorpus:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the defnition corpus")
            
            status = extract_definition_corpus(pg_connection, term_table, definition_table, document_table)
            
            if status:
                logging.info(f"Completed the extraction of the definition corpus and took {secondsToText(time()- start_time)}")
            else:
                logging.info(f"Definition extraction failed")           
            
    
    finally:
        pg_connection.dispose()


if __name__ == "__main__":
    main()