from config import *
from logical_layout_extraction import layout_extraction
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

        # parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-d", "--definitionextraction", help="extracting the logical structure of the document", action = "store_true" 
        )

        args = parser.parse_args()

        if args.definitionextraction:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the defnition of terms present in the celex documents started")
            
            status = process_records_in_batches(pg_connection)
            
            if status:
                logging.info(f"Completed the extraction of the structure of the celex documents and stored the information and took {secondsToText(time()- start_time)}")
            else:
                logging.info(f"Document extraction failed")
    
    finally:
        pg_connection.dispose()


if __name__ == "__main__":
    main()