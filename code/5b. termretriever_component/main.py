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
        
        data_split_table = metadata.tables['lexdrafter_energy_data_split']
        term_table = metadata.tables['lexdrafter_energy_definition_term']

        # parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-st", "--staticdefinitiondataset", help="Extracting the static definitions", action = "store_true" 
        )

        parser.add_argument(
            "-e", "--evaluationdataset", help="creating the split of the datasets", action = "store_true" 
        )

        parser.add_argument(
            "-f", "--evaluationdatasetfiltering", help="checking if the term is already defined", action = "store_true" 
        )

        parser.add_argument(
            "-s", "--evaluationdatasetscoring", help="Assign score to each sentence where term is present", action = "store_true" 
        )

        parser.add_argument('--split', help='split to be considered')

        args = parser.parse_args()

        if args.evaluationdataset:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the defnition of terms present in the celex documents started")
            
            status = process_records_in_batches(pg_connection, data_split_table, term_table)
            
            if status:
                logging.info(f"Completed the extraction of the structure of the celex documents and stored the information and took {secondsToText(time()- start_time)}")
            else:
                logging.info(f"Document extraction failed")
        
        if args.evaluationdatasetfiltering:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the defnition of terms present in the celex documents started")
            
            file_name = f'./dataset/{args.split}_split.json'
            # Read JSON file
            with open(file_name, 'r') as json_file:
                data = json.load(json_file)

            # Extract terms from JSON
            terms = [item['term'] for item in data]

            # Fetch existing celex_ids for terms from Postgresql
            existing_records = fetch_existing_celex_ids(pg_connection, data_split_table, term_table, terms)

            # Update JSON with existing_record field
            for item in data:
                term = item['term']
                if term in existing_records:
                    item['existing_record'] = existing_records[term]
                else:
                    item['existing_record'] = ["NEW TERM"]
            
            with open(f'./dataset/updated_{args.split}_split.json', 'w') as updated_json_file:
                json.dump(data, updated_json_file, indent=4)

        if args.evaluationdatasetscoring:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to assigning score to the statements where term exist")
            
            file_name = f'./dataset/updated_{args.split}_split.json'
            
            # Read JSON file
            with open(file_name, 'r') as json_file:
                updated_data = json.load(json_file)

            score_data = calculate_sentence_score(updated_data)

            # Save the updated JSON data with scores
            with open(f'./dataset/updated_{args.split}_split_score.json', 'w') as json_file:
                json.dump(score_data, json_file, indent=4)            
            
    
    finally:
        pg_connection.dispose()


if __name__ == "__main__":
    main()