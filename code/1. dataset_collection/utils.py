import logging
import dotenv


# Define a logger for this module
log = logging.getLogger(__name__)


def loadConfigFromEnv():
    """Loads configuration data from a dotenv file.

    This function searches for a `.env` file in the current working directory
    and, if found, reads its key-value pairs into a dictionary. The location
    of the found `.env` file and the number of key-value pairs are logged at
    the INFO level.

    Returns:
        dict: A dictionary containing the configuration data from the dotenv file,
              or an empty dictionary if no dotenv file is found.
    """

    dotenv_path = dotenv.find_dotenv()

    if dotenv_path:
        log.info(f"Found .env file at: {dotenv_path}")
        config = dotenv.dotenv_values(dotenv_path)
        log.info(f"Loaded {len(config)} key-value pairs from .env file.")
    else:
        log.warning(".env file not found. Using default configuration.")
        config = {}

    return config
