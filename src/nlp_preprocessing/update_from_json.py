import json
import logging
#from pathlib import Path
from typing import NamedTuple, Generator, List, Dict, Tuple
from typing import Optional, Any

from accessors import update_issue
from constants import JSON_ISSUE_FILE, JSON_UPDATE_FILE, IPS_FILE
from constants import DOILIST_FILE, DOI_EXCEPTIONS_FILE, DOWNLOAD_DIR


# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a file handler and set the log file path
log_file = "logs/log_doi2pdf.txt"
file_handler = logging.FileHandler(log_file)

# Configure the file handler
file_handler.setLevel(logging.INFO)  # Set the desired log level
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the file handler to the logger
logger.addHandler(file_handler)


# types
Articles = list[Dict[str,str]]
issue_data: list[Dict[str, str|Articles]] = []

# Load issue data from JSON (destination json)
with open("data/issue_data_output.json", "r") as file:
    issue_data = json.load(file)

# Load issue data from JSON (source json)
with open("data/issue_data_authyear.json", "r") as file:
    issue_data_source = json.load(file)

# error stores
ISSUE_READING_EXCEPTIONS: List[str] = []
ARTICLE_READING_EXCEPTIONS: List[Dict[str,str]] = []

# Iterate over each issue in the issue data source
for issue in issue_data_source:

    try:
        volume:str = issue["volume"]  # type: ignore
        issue_num:str = issue["issue"]    # type: ignore
        date:str = issue["date"]      # type: ignore
        issue_id = f"[vol:{volume} issue:{issue_num} date:{date}]"

        # Get the articles for the current issue
        articles:Articles = issue["articles"]  # type: ignore
    except Exception as e:
        ISSUE_READING_EXCEPTIONS.append(issue)
        logger.error(f"Error reading issue {issue}.")
        logger.exception(e)
        continue

    # Iterate over each article in the issue and get its doi
    for article in articles:

        try:
            # Get the DOI URL for the current article
            doi:str = article["doi"]

            # get author from source json
            author_year = article["author_year"]  # source

            # update author in issue data (ie copy from source to destination)
            for destination_issue in issue_data:
                same_volume = destination_issue["volume"] == volume
                same_issue_num = destination_issue["issue"] == issue_num
                if same_volume and same_issue_num:
                    update_issue(destination_issue, existing_doi_value=doi,
                                 new_author_value=author_year
                                 )

            #

            # pattern to match doi
            doi_pattern = r'([0-9]+\.[0-9]+\/[a-zA-Z0-9\.\-]+)'

        except Exception as e:
            ARTICLE_READING_EXCEPTIONS.append(article)
            logger.error(f"Error updating article with DOI {doi} from {issue_id}.")
            logger.exception(e)
            continue

logger.info(f"Exceptions re issue-reading: {len(ISSUE_READING_EXCEPTIONS)}.")
logger.info(f"Exceptions re article-reading: {len(ARTICLE_READING_EXCEPTIONS)}.")

## JSON data update

# Serialize the list of dictionaries to JSON string
json_data = json.dumps(issue_data, indent=4)

# Write the JSON string to a file
with open(JSON_UPDATE_FILE, 'w') as file:
    file.write(json_data)
