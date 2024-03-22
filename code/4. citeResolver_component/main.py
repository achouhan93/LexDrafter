from config import *
from tasks import *
from sqlalchemy import Table, MetaData
import utils
from time import time


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
    result = ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "") + \
             ("{0} hour{1}, ".format(hours, "s" if hours != 1 else "") if hours else "") + \
             ("{0} minute{1}, ".format(minutes, "s" if minutes != 1 else "") if minutes else "") + \
             ("{0} second{1}, ".format(round(seconds, 2), "s" if seconds != 1 else "") if seconds else "")
    return result


def main(argv=None):
    """
    Main function to orchestrate the execution of tasks based on command line arguments.
    
    This function initializes logging, processes command line arguments, and, if requested,
    performs citation resolution on the dataset, logging the process and execution time.
    
    Args:
        argv (list, optional): List of command line arguments.
    """
    try:
        # Load configuration from environment variables
        CONFIG = utils.loadConfigFromEnv()

        # Ensure the log directory exists
        if not os.path.exists(CONFIG["LOG_PATH"]):
            os.makedirs(CONFIG["LOG_PATH"])
            print(f'created: {CONFIG["LOG_PATH"]} directory.')

        # Configure logging
        logging.basicConfig(
            filename=CONFIG["LOG_EXE_PATH"],
            filemode="a",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%d-%m-%y %H:%M:%S",
            level=logging.INFO
            )

        # Establish a connection to the PostgreSQL database
        pg_connection = postgres_connection()

        # Reflect the database schema into MetaData and select the required table
        metadata = MetaData()
        metadata.reflect(pg_connection)
        definition_table = metadata.tables['lexdrafter_energy_term_explanation']

        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-c", "--citationresolution", help="creating the split of the datasets", action = "store_true" 
        )

        args = parser.parse_args()

        # Execute citation resolution if requested
        if args.citationresolution:
            start_time = time()
            logging.info(f"Current date and time: {secondsToText(start_time)}")
            logging.info("**********************************\n")
            logging.info(f"Process to extracting the citation terms present in the dynamic defnition fragments started")
            
            status = process_records_in_batches(pg_connection, definition_table)
            
            if status:
                logging.info(f"Completed the extraction of the citation present in the dynamic definition and stored the information and took {secondsToText(time()- start_time)}")
            else:
                logging.info(f"Citation extraction failed")
    
    finally:
        # Ensure the database connection is closed
        pg_connection.dispose()


if __name__ == "__main__":
    main()