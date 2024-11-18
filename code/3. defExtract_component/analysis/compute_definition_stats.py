"""
Compute stats such as compression ratio, lengths, n-gram novelty, etc.
This script relies entirely on the offline data.
"""

from typing import List, Union, Set
from collections import Counter
import regex

import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
import pandas as pd

from utils import *


def calculate_mean(numbers):
    if len(numbers) == 0:
        return None  # Avoid division by zero for empty lists
    else:
        total = sum(numbers)
        mean = total / len(numbers)
        return mean


if __name__ == "__main__":
    CONFIG = loadConfigFromEnv()

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

    pg_connection = postgres_connection(CONFIG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--definitionlengthanalysis",
        help="analysis of the length of definition explanantion",
        action="store_true",
    )

    args = parser.parse_args()

    if args.definitionlengthanalysis:
        total_count = 0
        train_celex_ids = set()
        validation_celex_ids = set()
        test_celex_ids = set()

        pg_read = PostgresReader(pg_connection)
        result_dataframe = pd.DataFrame()

        data = pg_read.get_information()
        result_rows = []

        for index, row in data.iterrows():
            if row["doc_id"] != 41:
                char_length = len(row["explanation"])
                token_length = compute_whitespace_split_length(row["explanation"])

                # Create a dictionary with the additional columns
                additional_columns = {
                    "id": row.name,
                    "char_length": char_length,
                    "token_length": token_length,
                }

                # Combine the existing row and additional columns
                combined_row = {**row, **additional_columns}

                # Append the combined row to the list
                result_rows.append(combined_row)

        # Append the additional columns to the result DataFrame
        result_dataframe = pd.DataFrame(result_rows)

        bar_plot(result_dataframe, "char_length")
        histogram_plot(
            result_dataframe["char_length"],
            xlim=(0, 1500),
            ylim=(0, 200),
            bins=50,
            fp="histogram_char_reference.png",
        )

        bar_plot(result_dataframe, "token_length")
        histogram_plot(
            result_dataframe["token_length"],
            xlim=(0, 200),
            ylim=(0, 200),
            bins=50,
            fp="histogram_token_reference.png",
        )
