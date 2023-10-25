import os
import json
import time
import random
import logging
import urllib.parse
from urllib.parse import urljoin, urlparse
from pathlib import Path
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from typing import NamedTuple, Generator, List, Dict, Tuple
from typing import Optional, Any
from dotenv import load_dotenv

from constants import JSON_ISSUE_FILE, JSON_UPDATE_FILE, IPS_FILE
from constants import DOILIST_FILE, DOI_EXCEPTIONS_FILE, DOWNLOAD_DIR

# Load environment variables from .env file
load_dotenv()

# Get IPs
IP_LIST:list[str] = []
# holds doi urls for pdf that failed to download
EXCEPTIONS:list[str] = []
SUCCESSES:list[str] = []
DOI_SOURCE_URL = os.getenv("DOI_SOURCE_URL")  # from .env file

with open(IPS_FILE, "r") as file:
    for line in file:
        ip = line.strip()
        IP_LIST.append(ip)

assert len(IP_LIST) == 100

Articles = list[Dict[str,str]]

# JSON data
issue_data: list[Dict[str, str|Articles]] = []
# Load issue data from JSON
with open(JSON_ISSUE_FILE, "r") as file:
    issue_data = json.load(file)

def rotate_proxy(ip_list:list[str]) -> Generator[str, None, None]:
    while True:
        for ip in ip_list:
            yield ip


def safe_slice(articles:Articles, start:int, end:int) -> Articles:
    """Proposes a fallback slicing in case of IndexError, and tries
    all the sub-slices of the current slice, checking if one of them
    is valid. If a valid slice is found, it is returned. Otherewise,
    the empty list is returned.
    """

    def slice_info(original_start:int, original_end:int, start:int, end:int) -> Any:
            # indicates if the original slicing indices are used (True), or
            # if the safe_slice has returned a proper sub-slice (False)
            different_indices:bool = original_start != start or original_end != end
            if different_indices:
                info = f"The required slice ({original_start}:{original_end}) is not valid. "
                info += f"We use sub-slice {start}:{end} to select the articles to be downoaded"
                logger.info(info)

    fallback_start:int = start
    fallback_end:int = end

    for i in range(start, end+1):
        for j in range(end, start-1, -1):
            try:
                result = articles[i:j]
                if result:
                    slice_info(start, end, fallback_start, fallback_end)
                    return result
            except IndexError:
                # Ignore the error and continue to the next combination
                pass

    # No valid slice found, return an empty list
    return []

def filter_articles(articles: Articles, criterion: str) -> Articles:
    """Filters an `articles` list according to various criteria, by
    selecting a slice of the original `articles` or randomly selecting
    a sample of 2, 3, or 5 articles.
    """

    # extracts two digits at the beginning of string and returns them as a tuple
    def extract_digits(string: str) -> Tuple[int|None,int|None]:
        first_digit = None
        second_digit = None

        if len(string) >= 2 and string[0].isdigit() and string[1].isdigit():
            first_digit = int(string[0])
            second_digit = int(string[1])

        return (first_digit, second_digit)

    # check if the criterion str begins with two digits
    fst, snd = extract_digits(criterion)
    if fst and snd:
        filtered_articles = safe_slice(articles, fst, snd)
        # return a non-empty slice of `articles[fst:snd]`
        if len(filtered_articles) == 2:
            return filtered_articles

    # Apply the filtering based on the provided criterion
    match criterion:
        case "rand2":
            return random.sample(articles, k=2)
        case "rand3":
            return random.sample(articles, k=3)
        case "rand5":
            return random.sample(articles, k=5)
        case _:
            # Default case if no matching criterion is found
            return articles


# Check if pdf file is already downloaded

def already_downloaded(pdf_filename):
    """Check if pdf file is already downloaded, by
    looking in the download directory and checking if
    any filename that can be found there matches the
    `pdf_filename` argument.
    Note: looks at DOWNLOAD_DIR (a filepath object)
    """

    article_exists = False
    # Iterate over the files in the download directory
    for existing_filename in os.listdir(DOWNLOAD_DIR):
        if existing_filename == pdf_filename:
            #print("  # FILENAME CHECK")
            #print("  # ==============")
            #print(f"pdf_filename: {pdf_filename}")
            #print(f"existing_filename: {existing_filename}")
            #print("  # ==============")
            article_exists = True
            break
    return article_exists

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


# Configure Selenium options

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode

# Create a new Chrome browser instance
browser = webdriver.Chrome(options=options)

# Load DOI list from file
with open(DOILIST_FILE, "r") as file:
    doi_list = file.read().splitlines()

# Create a generator to rotate proxies
proxy_generator = rotate_proxy(IP_LIST)



# global var for exception logging
pdf_url_current = ""

# Iterate over each DOI in the list
#for doi in doi_list:

# Iterate over each issue in the issue data
for issue in issue_data:

    volume:str = issue["volume"]  # type: ignore
    issue_num:str = issue["issue"]    # type: ignore
    date:str = issue["date"]      # type: ignore
    issue_id = f"[vol:{volume} issue:{issue_num} date:{date}]"

    # Get the articles for the current issue
    articles:Articles = issue["articles"]  # type: ignore
    # filter articles to download
    filtered_articles = filter_articles(articles, criterion="13")

    # Iterate over each article in the issue and get its doi
    for article in filtered_articles:

        # first check if we have registred a pdf file for this article
        if article["pdf"] != "":
            already_exists = f"Article already appears in our json data: {article['pdf']} {issue_id}. "
            already_exists += f"We move on without attempting a download."
            logger.info(already_exists)
            continue

        # Get the DOI URL for the current article
        doi:str = article["doi"]

        # Get the next proxy from the generator
        proxy = next(proxy_generator)
        options.add_argument(f'--proxy-server={proxy}')

        # Encode the DOI
        #encoded_doi = urllib.parse.quote(doi)
        try:
            url_with_doi = DOI_SOURCE_URL + doi # + encoded_doi
            logger.info(f"Started searching URL {url_with_doi}.")
            # Load the source website
            browser.get(url_with_doi)
        except Exception as e:
            wrong_url = f"Error downloading article with DOI {doi} from {pdf_url_current} {issue_id}."
            wrong_url += f"Unsuccessful attempt to extract pdf url from {DOI_SOURCE_URL}{doi}."
            logger.error(wrong_url)
            logger.exception(e)
            continue

        try:
            # Get the PDF URL
            pdf_url = browser.find_element(By.CSS_SELECTOR,'embed#pdf').get_attribute('src')
            # Example of inital pdf_url string (note: no https prefix & some extra '#navp...'):
            # "//source.com/journal-article/e08...cc2/lev1936.pdf#navpanes=0&view=FitH"

        except NoSuchElementException:
            # Handle the case when the PDF URL element is not found
            logger.info(f"Article likely not stored, since PDF URL not found for DOI: {doi} {issue_id}")
            EXCEPTIONS.append(doi)
            continue  # Skip to the next iteration without stopping the loop

        try:
            # Add the "https://" prefix if necessary
            if pdf_url is None:
                continue
            elif pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url

            # Remove any trailing fragment identifier
            pdf_url = urljoin(pdf_url, urlparse(pdf_url).path)
            pdf_url_current = pdf_url  # for exception logging

            # Extract filename from PDF URL
            filename = Path(pdf_url).stem
            # Modify the output filename format as needed
            # keep only the doi code
            doi_domain = "https://doi.org/10.1007/"
            doi_code:str = ""
            if doi.startswith(doi_domain):
                doi_code = doi[len(doi_domain):]
            else:
                no_prefix = f"Could not extract prefix '{doi_domain}' from DOI url {issue_id}. "
                no_prefix += f"Using the entire DOI url {doi} as part of the filename."
                logger.info(no_prefix)
                doi_code = doi
            output_filename = f"{filename}_{doi_code.replace('/', '_')}.pdf"
            article["pdf"] = output_filename
            article["txt"] = f"{filename}_{doi_code.replace('/', '_')}.txt"

            # check if we might not already have the pdf file in our pdf store
            if already_downloaded(article["pdf"]):
                already_exists = f"Pdf appears to be already downloaded: {article['pdf']} {issue_id}. "
                already_exists += f"We move on without attempting another download."
                logger.info(already_exists)
                continue

            # Download the PDF
            response = requests.get(pdf_url)
            # write it into the output file
            with open(DOWNLOAD_DIR / output_filename, 'wb') as file:  # type: ignore
                file.write(response.content)  # type: ignore

            SUCCESSES.append(f"  + {issue_id} -- {pdf_url}")
            logger.info(f"Downloaded article with DOI {doi} from {pdf_url} {issue_id}.")
            #print(f"Downloaded article with DOI: {doi}")

        except Exception as e:
            EXCEPTIONS.append(doi)
            logger.error(f"Error downloading article with DOI {doi} from {pdf_url_current} {issue_id}.")
            logger.error(f"Unsuccessful attempt to extract pdf url from {DOI_SOURCE_URL}{doi}.")
            logger.exception(e)
            continue
            #print(f"Error downloading article with DOI: {doi}")
            #print(str(e))

# Close the browser and clean up resources
try:
    browser.quit()
except Exception as e:
    logger.warning("Error while quitting the browser.")
    logger.exception(e)


## Successes

if len(SUCCESSES) > 0:
    logger.info(f"  # Downloaded successfully {len(SUCCESSES)} pdf files:")
    for s in SUCCESSES:
        logger.info(s)

## JSON data update

# Serialize the list of dictionaries to JSON string
json_data = json.dumps(issue_data, indent=4)

# Write the JSON string to a file
with open(JSON_UPDATE_FILE, 'w') as file:
    file.write(json_data)


## Exceptions

def write_list(lines: List[str], file_path: str) -> None:
    with open(file_path, "a") as file:
        file.writelines(line + "\n" for line in lines)

if len(EXCEPTIONS) > 0:
    write_list(EXCEPTIONS, DOI_EXCEPTIONS_FILE)
    logger.info(f"  # Download failed for {len(EXCEPTIONS)} DOIs; see ./exceptions_doi.txt")
