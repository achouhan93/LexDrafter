from typing import List, Union, Optional, Tuple
import regex

from tqdm import tqdm
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import logging
import dotenv
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy import Table, MetaData, select, func, or_, Integer, and_, desc

# Set larger font size for plots
matplotlib.rc('xtick', labelsize=18)
matplotlib.rc('ytick', labelsize=18)
matplotlib.rc('legend', fontsize=18)
# set LaTeX font
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

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


def postgres_connection(CONFIG):
    """
    Establish the postgresql connection

    Returns:
        object: postgresql connection object
    """
    # Postgresql Connection
    PG_USER = CONFIG['PG_USER']
    PG_PWD = CONFIG['PG_PWD']
    PG_DATABASE = CONFIG['PG_DATABASE']
    PG_SERVER = CONFIG['PG_SERVER']
    PG_HOST = CONFIG['PG_HOST']

    connection_string = f'postgresql://{PG_USER}:{PG_PWD}@{PG_SERVER}:{PG_HOST}/{PG_DATABASE}'
    connect_args = {'options': '-csearch_path=public'}
    database_engine = create_engine(connection_string, connect_args=connect_args, poolclass=QueuePool, pool_size=10, max_overflow=20)
    return database_engine


def compute_whitespace_split_length(text: str) -> int:
    return len(text.split(" "))


def histogram_plot(lengths: List[Union[int, float]],
                   xlim: Optional[Union[List, Tuple]] = (0, 20000),
                   ylim: Optional[Union[List, Tuple]] = (0, 150),
                   bins: int = 20,
                   fp: str = "./histogram.png"
                   ):
    plt.hist(lengths, range=xlim, bins=bins, color='#1b9e77', label="# of documents")
    plt.xlim(xlim)
    plt.ylim(ylim)

    # Mean and std lines
    plt.axvline(np.mean(lengths), color='r', linestyle='solid', linewidth=2, label='Mean')
    plt.axvline(np.mean(lengths) - np.std(lengths), color='g', linestyle='dotted', linewidth=1, label='Std Dev' )
    plt.axvline(np.mean(lengths) + np.std(lengths), color='g', linestyle='dotted', linewidth=1)

    # Title and save
    plt.savefig(fp, dpi=300)
    plt.show()
    plt.close()


def bar_plot(df, column):
    # Count the frequency of each attribute value
    counts = df[column].value_counts().sort_index()

    # Calculate the mean and standard deviation for each attribute
    mean = df[column].mean()
    std_length = df[column].std()

    # # Create a bar plot for Fragment Length
    fig, ax = plt.subplots()
    ax.bar(counts.index, counts.values, label="Frequency", color="#1b9e77")
    ax.axvline(mean, color='r', linestyle='solid', linewidth=2, label='Mean')
    ax.axvline(mean + std_length, color='g', linestyle='dashed', linewidth=2, label='Std Dev')
    ax.axvline(mean - std_length, color='g', linestyle='dashed', linewidth=2)
    ax.set_xlabel(f'Definition tokens')
    ax.set_ylabel('Number of Documents')
    # ax.set_title('Distribution of definitions in Energy domain')
    ax.legend()
    ax.set_xlim(min(counts.index)-1, max(counts.index)+1)
    plt.savefig(f"{column}_distribution.png", dpi=400)
    plt.show()


class PostgresReader():

    def __init__(self, pg_connection):
        self.engine = pg_connection

        metadata = MetaData()
        metadata.reflect(pg_connection)
    
        self.explanation_table = metadata.tables['lexdrafter_energy_term_explanation']

    def get_information(self):
        doc_query = (self.explanation_table.select())

        with self.engine.connect().execution_options(stream_results=True) as conn:
            doc_results = conn.execution_options(stream_results=True).execute(doc_query)

            data = {
                'term_id': [],
                'doc_id': [],
                'explanation': []
            }

            while True:
                results_chunk = doc_results.fetchmany(20000)
                
                if not results_chunk:
                    break

                for row in results_chunk:
                    data['term_id'].append(row[1])
                    data['doc_id'].append(row[2])
                    data['explanation'].append(row[3])
        df = pd.DataFrame(data)

        return df