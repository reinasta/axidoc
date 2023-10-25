"""
Web scrapes a journal's volume, issue, date info from a page that lists all
volume and issue data.
It writes these as fields in issue_data.json, along with an empty `articles` field
to be upldated in a different script that web scrapes the pages of individual
journal issues
"""

import re
import json
from datetime import datetime
from typing import Optional, NamedTuple, List, Any
from selenium import webdriver
from bs4 import BeautifulSoup
from collections import namedtuple


# Selenium

# Configure Selenium options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode
#PROXY = "195.248.240.25"
#options.add_argument(f'--proxy-server={PROXY}')

# Create a new Chrome browser instance
browser = webdriver.Chrome(options=options)

# URL for the volumes of issues page, which contains a list of all issues of the journal
url_volumes_and_issues = "https://link.springer.com/journal/11336/volumes-and-issues"

try:

    # URL of a specific issue page
    browser.get(url_volumes_and_issues)
    # Get the HTML content of the volumes and issues page
    html_volumes_and_issues = browser.page_source

    # Close the driver
    browser.quit()

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_volumes_and_issues, 'html.parser')
    # get list times containing volume and issue number information
    list_items = soup.find_all("li", class_="c-list-group__item")
    print(f"list items found: {len(list_items)}")
    # Pattern to match the volume and issue numbers in the href string
    pattern = r"/journal/11336/volumes-and-issues/(\d+)-(\d+)"

    # Extract the volume and issue numbers using regular expressions
    VolumeIssue = namedtuple("VolumeIssue", ["volume", "issue", "url", "date", "articles"])
    issue_data = []
    for item in list_items:
        a_tag = item.find("a", class_="u-interface-link")
        if a_tag:
            date_text = a_tag.get_text(strip=True).split(',')[0]
            date_object = datetime.strptime(date_text, '%B %Y')
            date_string = date_object.strftime('%Y-%m-%d')
            href = a_tag["href"]
            match = re.search(pattern, href)
            if match:
                volume = match.group(1)
                issue = match.group(2)
                url_base = "https://link.springer.com/journal/11336/volumes-and-issues/"
                url_issue = url_base + f"{volume}-{issue}"
                print(f"url: {url_issue}")
                d = VolumeIssue(volume=volume,
                                issue=issue,
                                url=url_issue,
                                date=date_string,
                                articles=[]  # this will be filled at a later stage
                                )
                issue_data.append(d)
            else:
                raise ValueError("No volume and issue match!")

    # Convert named tuples to dictionaries
    issue_dicts = [dict(issue._asdict()) for issue in issue_data]
    # Serialize the list of dictionaries to JSON string
    json_data = json.dumps(issue_dicts, indent=4)

    # Write the JSON string to a file
    with open('issue_data.json', 'w') as file:
        file.write(json_data)

    # 353 issue dicts in total
    print(f"Wrote {len(issue_dicts)} issue dicts to file ./issue_data.json")

finally:
    # Close the browser
    browser.quit()
