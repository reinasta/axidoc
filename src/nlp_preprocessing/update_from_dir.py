"""
Updates the json datastore with pdf filenames picked from the
pdf datastore -- this might be useful if we downloaded some
pdf files on the side, but note that these pdf files need to
have filenames with the expected formatting, which includes
author, year, and DOI, like this:

 - richardson1936_10.1007_BF02287926.pdf
 - green1950_10.1007_BF02289178.pdf

"""
import os
import json
import logging
from typing import List

from constants import DOWNLOAD_DIR, JSON_ISSUE_FILE

# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a file handler and set the log file path
log_file = "logs/log_update_from_dir.txt"
file_handler = logging.FileHandler(log_file)

# Configure the file handler
file_handler.setLevel(logging.INFO)  # Set the desired log level
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the file handler to the logger
logger.addHandler(file_handler)

# lists
UPDATED:List[str] = []
EXCEPTIONS:List[str] = []

# Load the JSON issue file
with open(JSON_ISSUE_FILE) as file:
    issue_data = json.load(file)

# Iterate over the files in the download directory
for filename in os.listdir(DOWNLOAD_DIR):
    # Extract DOI from the filename like "green1950_10.1007_BF02289178.pdf"
    splits = filename.replace(".pdf", "").split("_")
    # check right formatting
    try:
        assert len(splits) == 3
    except AssertionError:
        EXCEPTIONS.append(filename)
        logger.error(f"UpdateFromDir: Filename not formatted as expected: {filename}")
        logger.info(f"UpdateFromDir: Right formatting example: green1950_10.1007_BF02289178.pdf")
        continue
    # if no exception, go ahead and rebuild the DOI code
    # basename = splits[0]
    doi = splits[1] + '/' + splits[2]

    # Iterate over the issues and articles in the JSON file
    for issue in issue_data:
        for article in issue["articles"]:
            # Check if the current article has an empty "pdf" value and matching DOI
            if article["pdf"] == "" and doi in article["doi"]:
                # Update the "pdf" value with the filename
                article["pdf"] = filename
                UPDATED.append(filename)

# Update the JSON issue file with the modified data
with open(JSON_ISSUE_FILE, "w") as file:
    json.dump(issue_data, file, indent=4)

if len(UPDATED) > 0:
    logger.info(f"  # Updated {len(UPDATED)} article entries with the following .pdf filenames:")
    for filename in UPDATED:
        logger.info(f"    + {filename}")
if len(EXCEPTIONS) > 0:
    print(f"  # There are {len(EXCEPTIONS)} pdf files with invalid filename formatting:")
    for filename in EXCEPTIONS:
        logger.info(f"    + {filename}")
