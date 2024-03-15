import logging
import dotenv


# Define a logger for this module
log = logging.getLogger(__name__)


def loadConfigFromEnv():
    """
    Loads configuration data from a .env file.

    This function searches for a .env file in the current or parent directories,
    loads its configuration variables into a dictionary, and logs information
    about the found configuration values.

    Returns:
        dict: A dictionary containing the loaded configuration data.
    """

    DOTENVPATH = dotenv.find_dotenv()
    CONFIG = dotenv.dotenv_values(DOTENVPATH)

    log.info(f"found .env file at {DOTENVPATH}")
    log.info(f"found {len(CONFIG)} key-value pairs in .env file")
    log.info(f"found .env file at {DOTENVPATH}")
    log.info(f"found {CONFIG} key-value pairs in .env file")

    return CONFIG
