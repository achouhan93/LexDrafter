## Citation Extraction from Dynamic Definition

### Overview
In dynamic definition fragments, reference is made to another legislative document. So the task of CiteResolver is to resolve the citation and add the information about cited document in the `reference_list` of the definition fragment.

### Features
- **Extraction of Citation Information Term**: Parses and extracts the citation information present in the definition fragment.
- **Database Interaction**: Utilizes PostgreSQL databases for extracting and storing definition fragment information.
- **Logging and Progress Tracking**: Provides detailed logging and progress tracking for document processing.

### Requirements
- Python 3.x
- PostgreSQL databases
- Python packages: `sqlalchemy`, `tqdm`, `regex`, `psycopg2`

### Setup and Configuration
1. **Environment Configuration**: Store database configurations and other settings in environment variables or a configuration file.
2. **Database Setup**: Ensure that PostgreSQL database is up and running, and accessible from the system where the script is executed.
3. **Python Environment**:
    - Install required Python packages:
    ```
    pip install sqlalchemy tqdm regex psycopg2
    ```
4. **Logging Configuration**: The system uses Python's `logging` module to log the processing status and errors. Configure the log file path in the environment variables or the configuration file.

### Usage
Before execution of the python script, make sure that defExtract component scripts are executed and definition corpus is built. If definition corpus is not yet created refer to the script present at [`code/3. defExtract_component`](https://github.com/achouhan93/LexDrafter/blob/main/code/3.%20defExtract_component). After definition corpus is created execute the `main` script to resolve citations present in the dynamic definitions. This can be done from the command-line with command-line arguments to specify additional functionalities or processing modes. For example, to initiate the extraction of citation information:
```cmd
python main.py --citationresolution
```

### How It Works
The system operates in several steps:
1. **Connection Establishment**: Establishes connections to PostgreSQL database.
2. **Definition Fragment Fetching**: Retrieves definition fragment that are dynamic in nature from Postgres.
3. **Citation Resolution**:
    - Parses the definition fragment.
    - Extract the citation information and populate the `reference_list` field of the definition fragment.
4. **Information Storage**: Stores the extracted information into a PostgreSQL database in a structured format.
5. **Logging and Progress Tracking**: Logs the process steps and tracks the progress of document processing.