import logging
import dotenv

log = logging.getLogger(__name__)


def loadConfigFromEnv():
    """_summary_

    Returns:
        dict: loads all configration data from dotenv file
    """

    DOTENVPATH = dotenv.find_dotenv()
    CONFIG = dotenv.dotenv_values(DOTENVPATH)

    log.info(f"found .env file at {DOTENVPATH}")
    log.info(f"found {len(CONFIG)} key-value pairs in .env file")
    log.info(f"found .env file at {DOTENVPATH}")
    log.info(f"found {CONFIG} key-value pairs in .env file")

    return CONFIG
