## EUR-Lex Document Extractor Script

This script extracts and inserts [EUR-Lex]((https://eur-lex.europa.eu/) documents into a specified OpenSearch index based on user-provided parameters.

### **Functionality:**

* Supports extraction by time range (specified year span) or by domain numbers.
* Leverages `opensearch-python` for database interaction.
* Provides informative logging and error handling.

### **Usage:**

#### Run the script:

```bash
python eurlex_extraction.py [--range <start_year> <end_year>] [--domain <domain_number> ...]
                             [--minyear <min_year>] [--maxyear <max_year>]
```

**Choose extraction mode:**

`--range`: Extracts documents for a specified year range.
`--domain`: Extracts documents for specified domains within a year range.

**Specify date range:**

`--minyear`: Minimum year for extraction (default: 1948).
`--maxyear`: Maximum year for extraction (default: current year).

#### Example Usage

1. Extract documents for all domains from 2020 to 2022:

```bash
python main.py --range --minyear 2020 --maxyear 2022
```

2. Extract documents for domain 12, i.e., energy domain:

```bash
python main.py --domain 12
```

#### Additional Information
Logs are stored in the `LOG_PATH` directory (specified in environment variables). The script processes documents in batches of 100 by default. The script checks for existing documents in the database before extraction to avoid duplicates.


:exclamation: **Note: For troubleshooting or more details on specific functions, refer to the script's code comments or functions docString.**