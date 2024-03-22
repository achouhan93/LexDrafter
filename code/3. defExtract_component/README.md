## Building Definition Corpus

### Overview
For building definition corpus, first `Definitions` article is identified in a document, followed by extracting the definitions, similar to the approach proposed by [Damaratskaya 2023](https://mediatum.ub.tum.de/1656157?query=Anastasiya&show_id=1715461). The `DefExtract` component identifies the the definitions present in the `Definitions` article as:
- '...' means ...; (static definition)
- '...' means ... as defined in [reference to the static definition]; (dynamic definition)

These information are stored in Postgres tables where:
- `lexdrafter_energy_term_explanation` stores the term_id and the definition, and
- `lexdrafter_energy_definition_term` stores the term_id and the term, this table also stores the occurences of the term present in sentences present in the different articles. As a context for definition generation, one can use this information or can also query the OpenSearch for the respective term used in the sentences.


### Features
- **Extraction of Definition Term**: Parses and extracts the term and its definition from `Definitions` article present in the document.
- **Batch Processing**: Processes one celex document at a time. The celex IDs are obtained from the OpenSearch.
- **Database Interaction**: Utilizes both OpenSearch and PostgreSQL databases for extracting and storing document information, respectively.
- **Logging and Progress Tracking**: Provides detailed logging and progress tracking for document processing.

### Requirements
- Python 3.x
- OpenSearch and PostgreSQL databases
- Python packages: `sqlalchemy`, `beautifulsoup4`, `tqdm`, `regex`, `matplotlib`, `psycopg2`

### Setup and Configuration
1. **Environment Configuration**: Store database configurations and other settings in environment variables or a configuration file.
2. **Database Setup**: Ensure that both OpenSearch and PostgreSQL databases are up and running, and accessible from the system where the script is executed.
3. **Python Environment**:
    - Install required Python packages:
    ```
    pip install beautifulsoup4 sqlalchemy tqdm regex matplotlib psycopg2
    ```
4. **Logging Configuration**: The system uses Python's `logging` module to log the processing status and errors. Configure the log file path in the environment variables or the configuration file.

### Usage
Before execution of the python script, make sure that the database is created and tables are created. Refer to the [`database_definitionCorpus_schema.sql`](https://github.com/achouhan93/LexDrafter/blob/main/code/3.%20defExtract_component/tasks/database/database_definitionCorpus_schema.sql) script to create the database. After database creation execute the `main` script to create the definition corpus. This can be done from the command-line with command-line arguments to specify additional functionalities or processing modes. For example, to initiate the extraction of the definitions from the legislative documents:
```cmd
python main.py --definitionextraction
```

After the population of the table with the definition information, to obtain histogram of the distribution of definition word lengths, execute the [`analysis/compute_definition_stats.py`](https://github.com/achouhan93/LexDrafter/blob/main/code/3.%20defExtract_component/analysis/compute_definition_stats.py) script.


### How It Works
The system operates in several steps:
1. **Connection Establishment**: Establishes connections to OpenSearch and PostgreSQL databases.
2. **Document Fetching**: Retrieves document ids from OpenSearch that have not been processed yet.
3. **Definition Term Processing**:
    - Parses the content of each document.
    - Extracts the `Definitions` article.
    - Extract the term and its definition along with sentences present in the document using that term.
4. **Information Storage**: Stores the extracted information into a PostgreSQL database in a structured format.
5. **Logging and Progress Tracking**: Logs the process steps and tracks the progress of document processing.