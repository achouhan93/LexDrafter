## CELEX Document Processing System

### Overview
The CELEX Document Processing System is designed to extract structural information from CELEX documents stored in an OpenSearch database and subsequently store this information into a PostgreSQL database. This process involves parsing HTML content of documents, extracting logical structures such as titles, recitals, chapters, sections, articles, and annexes, and processing documents in batches for efficiency.

### Features
- **Extraction of Logical Structures**: Parses and extracts structured information from CELEX documents.
- **Batch Processing**: Processes documents in batches, handling large datasets efficiently.
- **Database Interaction**: Utilizes both OpenSearch and PostgreSQL databases for extracting and storing document information, respectively.
- **Logging and Progress Tracking**: Provides detailed logging and progress tracking for document processing.

### Requirements
- Python 3.x
- OpenSearch and PostgreSQL databases
- Python packages: `sqlalchemy`, `beautifulsoup4`, `tqdm`, `regex`, `matplotlib`

### Setup and Configuration
1. **Environment Configuration**: Store database configurations and other settings in environment variables or a configuration file.
2. **Database Setup**: Ensure that both OpenSearch and PostgreSQL databases are up and running, and accessible from the system where the script is executed.
3. **Python Environment**:
    - Install required Python packages:
    ```
    pip install beautifulsoup4 sqlalchemy tqdm regex matplotlib
    ```
4. **Logging Configuration**: The system uses Python's `logging` module to log the processing status and errors. Configure the log file path in the environment variables or the configuration file.

### Usage
To run the document processing system, execute the `main` function in the script. This can be done from the command-line with command-line arguments to specify additional functionalities or processing modes. For example, to initiate the extraction of the logical structure of documents:
```cmd
python main_script.py --schemacreation
```

### How It Works
The system operates in several steps:
1. **Connection Establishment**: Establishes connections to OpenSearch and PostgreSQL databases.
2. **Document Fetching**: Retrieves documents from OpenSearch that have not been processed yet.
3. **Document Processing**:
    - Parses the HTML content of each document.
    - Extracts structural information.
4. **Information Storage**: Stores the extracted information into a PostgreSQL database in a structured format.
5. **Logging and Progress Tracking**: Logs the process steps and tracks the progress of document processing.