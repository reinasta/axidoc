"""
This fills in info about articles in each per issue (and volume).
This information is stored in the `articles` value (a list of
dictionaries containing fields `doi`, `pdf`, and `txt`, where the
latter two will store filenames for the articles, once we download
the pdf files and convert them to text files.)
"""

import re
import json
import logging
from typing import Optional, Tuple, NamedTuple, List, Dict, Any
from selenium import webdriver
from bs4 import BeautifulSoup  # type: ignore
from collections import namedtuple

from accessors import update_issue
from constants import IPS_FILE, JSON_ISSUE_FILE, JSON_UPDATE_FILE

# CHANING INPUT AND OUTPUT FILES
# Note: we update from the update file (this is currently most up to date)
JSON_ISSUE_FILE = JSON_UPDATE_FILE
# we temporarily redirect author-year-related updates to a new update file
JSON_UPDATE_FILE = "data/issue_data_authyear.json"

WARNINGS:List[str] = []

# Get IPs
IP_LIST = []

with open(IPS_FILE, "r") as file:
    for line in file:
        ip = line.strip()
        IP_LIST.append(ip)

assert len(IP_LIST) == 100

# holds all doi urls
ALL_DOIS:list[str] = []

# URL of the web page to retrieve
#url_issue = 'https://link.springer.com/journal/11336/volumes-and-issues/16-2'


# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create a file handler and set the log file path
log_file = "logs/log_url2doi.txt"
file_handler = logging.FileHandler(log_file)

# Configure the file handler
file_handler.setLevel(logging.INFO)  # Set the desired log level
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the file handler to the logger
logger.addHandler(file_handler)




# html body div.c-page-layout li.c-list-group__item h3.c-card__title a[href]
# ul.u-list-reset ul.c-list-group li.c-list-group__item

def dois_per_issue(html_issue:str) -> list[str]:
    """ An 'issue' html page contains a list of links to articles. This
    function extracts DOI urls from the links.
    """

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_issue, 'html.parser')
    list_items = soup.find_all("li", class_="c-list-group__item")

    # store href attributes
    dois:list[str] = []
    doi_pattern = r'([0-9]+\.[0-9]+\/[a-zA-Z0-9\.\-]+)'

    # `ul.u-list-reset ul.c-list-group li.c-list-group__item`
    # Extract the href value from the <a> elements within the <h3> elements
    for li in list_items:
        h3 = li.find('h3', class_='c-card__title')
        if h3:
            link = h3.find('a')
            if link:
                href = link.get('href')
                doi_domain:str = "https://doi.org/"
                match_obj = re.search(doi_pattern, href)
                if match_obj is None:
                    logger.info(f"Url2Doi: no DOI found in href={href}.")
                    raise ValueError('Url2DoiError: DOI could not be matched')
                doi_match:str = match_obj.group(1)

                doi:str = doi_domain + doi_match
                dois.append(doi)
                #print(doi)
    return dois

#main-content > div > div > div.u-text-sans-serif > div.c-box.c-box--shadowed.u-mb-48 > ol > li:nth-child(1) > article > div.c-card__body.app-card-body > div > ul > li:nth-child(1) > span

def authors_per_issue(html_str:str) -> List[List[str]]:
    """Parses the html 'issue' page containing articles of an issue and
    extracts a list of authors for each of the articles, then
    returns the result in a list -- a list of lists of authors.
    """
    author_lists:List[List[str]] = []
    soup = BeautifulSoup(html_str, 'html.parser')
    selector = '#main-content div.c-box > ol.app-volumes-and-issues__article-list >'
    selector += 'li.c-list-group__item > article.c-card > div.app-card-body '
    selector += 'ul.c-author-list'
    author_uls = soup.select(selector)

    for ul in author_uls:
        authors = []
        for li in ul.find_all('li'):
            author = li.find('span').text.strip()
            authors.append(author)
        author_lists.append(authors)

    return author_lists

# #main-content > div > div > div.u-text-sans-serif > div.c-box.c-box--shadowed.u-mb-48 > ol > li:nth-child(7)
def doisnauthors(html_str: str) -> Tuple[List[Tuple[str, List[str]]], Dict[str,int]]:
    """Collects doi of article and its authors for each article of an issue.
    Returns a list of (doi, authors) and a dict storing the number of empty
    values (empty string dois, and 'anon' authors) for all articles of the issue.
    """

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_str, 'html.parser')
    selector = '#main-content div.c-box > ol.app-volumes-and-issues__article-list >'
    selector += 'li.c-list-group__item > article.c-card > div.app-card-body'
    doi_path = 'h3.c-card__title > a'
    author_path = 'ul.c-author-list'

    # doi pattern
    dois_and_authors:List[Tuple[str,List[str]]] = []

    empty_values:Dict[str,int] = {"doi": 0, "authors": 0}
    doi_pattern = r'([0-9]+\.[0-9]+\/[a-zA-Z0-9\.\-]+)'

    for article_card in soup.select(selector):
        ul = article_card.select_one(author_path)
        a = article_card.select_one(doi_path)
        # vars
        authors:List[str] = []
        doi:str = ""

        # Process the ul and a elements as needed
        if ul:
            # ul element found, do something
            for li in ul.find_all('li'):
                author = li.find('span').text.strip()
                authors.append(author)

        if a:
            # a element found, do something
            href = a.get('href')
            doi_domain:str = "https://doi.org/"
            match_obj = re.search(doi_pattern, href)
            if match_obj is None:
                logger.info(f"Url2Doi: no DOI found in href={href}.")
                raise ValueError('Url2DoiError: DOI could not be matched')
            doi_match:str = match_obj.group(1)
            doi = doi_domain + doi_match

        # provide default author value; if doi is the empty str, we leave it as is
        if not bool(authors):
            authors = ['anon anon']
            empty_values["authors"] += 1
        if doi == "":
            empty_values["doi"] += 1

        dois_and_authors.append((doi,authors))
        doi, authors = "", []  # reset values

    return (dois_and_authors, empty_values)

    # li.c-list-group__item > article.c-card > div.c-card__body.app-card-body
    ### h3.c-card__title > a
    ### div.u-mb-8 > ul.c-author-list



    return None

def dois_and_authors(html_str: str) -> None|List[Tuple[str, List[str]]]:
    dois = dois_per_issue(html_str)
    author_lists = authors_per_issue(html_str)
    try:
        dois_n_authors = list(zip(dois,author_lists, strict=True))
    except ValueError:
        logger.error(f"Lengths of dois ({len(dois)}) and authors ({len(author_lists)}) differ.")
        info = ""
        for i in range(0, max(len(dois),len(author_lists))):
            if dois[i] is not None:
                doi = dois[i]
            else:
                doi = "MISSING_DOI"
            if author_lists[i] is not None:
                author = author_lists[i]
            else:
                "MISSING_AUTHORS"
            info += f"{doi}\t{author}\n"
        logger.info(f"Here is a list of dois and author-lists:\n{info}")
        return None

    return dois_n_authors

def write_list(lines: List[str], file_path: str) -> None:
    with open(file_path, "w") as file:
        file.writelines(line + "\n" for line in lines)

def rotate_proxy(ip_list):
    while True:
        for ip in ip_list:
            yield ip


# Configure Selenium options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode

# Create a new Chrome browser instance
browser = webdriver.Chrome(options=options)

Articles = list[Dict[str,str]]

issue_data: list[Dict[str, str|Articles]] = []
# Load issue data from JSON
with open(JSON_ISSUE_FILE, "r") as file:
    issue_data = json.load(file)

# Create a generator to rotate proxies
proxy_generator = rotate_proxy(IP_LIST)

# Initialize a list to store all DOIs
ALL_DOIS = []
EXCEPTIONS:list[Dict[str, str|Articles]] = []

# Iterate over each issue in the issue data
for issue in issue_data:

    # get existing issue fileds
    volume = issue["volume"]
    if isinstance(issue["date"], str):
        date:str = issue["date"]
    else:
        logger.error(f"Invalid date string: {issue['date']}")
    issue_number = issue["issue"]
    url = issue["url"] if isinstance(issue["url"], str) else ""
    if len(url) == 0:
        raise ValueError("Empty url is invalid!")
    #articles:Articles = []
    #if isinstance(issue["articles"], list):
    #    articles = issue["articles"]
    #    for article in articles:
    #        assert isinstance(article, dict)
    #else:
    #    logger.error("Value of articles={issue['articles']} should be a list of dicts!")
    #logger.info(f"Starting checking Vol. {volume} Issue {issue_number} ...")

    try:
        # Get the next proxy from the generator
        proxy = next(proxy_generator)
        options.add_argument(f'--proxy-server={proxy}')

        # Load the URL with Selenium
        browser.get(url)

        # Get the page source (HTML) from Selenium
        html = browser.page_source

        # Apply the function to extract DOIs & authors from the HTML
        dois_n_authors, empty_values = doisnauthors(html)
        if empty_values["doi"] > 0:
            missing_doi = f"Empty DOI for Vol. {volume} Issue {issue_number}."
            logger.info(missing_doi)
        if empty_values["authors"] > 0:
            missing_authors = f"Empty author (replaced with 'anon') "
            missing_authors += f"for Vol. {volume} Issue {issue_number}."
            logger.info(missing_authors)

        dois = [tup[0] for tup in dois_n_authors]
        ALL_DOIS += dois
        author_year_strs = []
        logger.info(f"Start writing author-info for {volume} Issue {issue_number} ...")
        for tup in dois_n_authors:
            doi, authors = tup
            # stores the first author's surname and article creation date (year)
            author_year = authors[0].split()[-1] + date.split('-')[0]
            author_year_strs.append(author_year)

            # fill in the article fields
            #article_obj = {"doi": doi, "author_year": author_year, "pdf": "", "txt": ""}
            #issue["articles"] = []
            #issue["articles"].append(article_obj)  # type: ignore

            # in issue, update article (identified using existing doi) with author info
            update_issue(issue=issue, existing_doi_value=doi,
                        new_author_value=author_year)


        # Print info about extracted data per issue
        summary = f" # Processed Volume: {volume}, Issue: {issue_number}, "
        summary += f"Date: {date}, DOIs: {len(dois)}, "
        summary += f"author_year strings: {', '.join(author_year_strs)}."
        logger.info(summary)

    except Exception as e:
        logger.error(f"Error processing issue {volume}-{issue_number} with proxy {proxy}.")
        logger.exception(e)
        EXCEPTIONS.append(issue)

# Close the driver
browser.quit()

## Doi list

# 3703 DOIs
write_list(ALL_DOIS, 'doilist.txt')
print(f"  # Processed {len(ALL_DOIS)} DOIs to be found in ./doilist.txt")

## Update json data

# Serialize the list of dictionaries to JSON string
json_data = json.dumps(issue_data, indent=4)

# Write the JSON string to a file
with open(JSON_UPDATE_FILE, 'w') as file:
    file.write(json_data)

print(f"  # Note: we also updated {JSON_UPDATE_FILE} with the processed DOIs and authors (find them under the 'articles' field)!")

## Exceptions

if len(EXCEPTIONS) > 0:
    # Serialize the list of dictionaries to JSON string
    json_exceptions = json.dumps(EXCEPTIONS, indent=4)
    # Write the JSON string to a file
    with open('exceptions.json', 'w') as file:
        file.write(json_exceptions)
    print(f"  # Exceptions: {len(EXCEPTIONS)} errors in DOI-processing  written to file ./exceptions.json")

if len(WARNINGS) > 0:
    print(f"  # Warnings: {len(WARNINGS)} issues (e.g. empty values): ")
    for w in WARNINGS:
        print(f"    + {w}")
