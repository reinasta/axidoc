import json
from typing import Dict, List

from constants import JSON_ISSUE_FILE, JSON_UPDATE_FILE, IPS_FILE
from constants import DOILIST_FILE, DOI_EXCEPTIONS_FILE, DOWNLOAD_DIR

# Load issue data from JSON
with open("data/issue_data_authyear.json", "r") as file:
    issue_data = json.load(file)

Articles = List[Dict[str, str]]
IssueData = List[Dict[str, str|Articles]]

def get_doi(article: Dict[str, str]) -> str:
    return article.get('doi', '')

def get_author(article: Dict[str, str]) -> str:
    return article.get('author_year', '')

def get_pdf(article: Dict[str, str]) -> str:
    return article.get('pdf', '')

def get_text(article: Dict[str, str]) -> str:
    return article.get('txt', '')

def update_doi(article: Dict[str, str], new_doi: str) -> None:
    article['doi'] = new_doi

def update_author(article: Dict[str, str], new_author: str) -> None:
    article['author_year'] = new_author

def update_pdf(article: Dict[str, str], new_pdf: str) -> None:
    article['pdf'] = new_pdf

def update_text(article: Dict[str, str], new_text: str) -> None:
    article['txt'] = new_text

# Example usage
issue_data_sample: IssueData = [
    {
        'volume': '1',
        'issue': '1',
        'url': 'https://example.com',
        'date': '2023-06-30',
        'articles': [
            {'doi': '10.1234/article1', 'pdf': 'article1.pdf',
             'text': 'Lorem ipsum', 'author_year': 'joe1987'
            },
            {'doi': '10.5678/article2', 'pdf': 'article2.pdf',
             'text': 'Dolor sit amet',  'author_year': 'collins1999'
             }
        ]
    },
    # ...
]

dois:List[str] = []
authors:List[str] = []
pdfs:List[str] = []
texts:List[str] = []

missing_dois:List[str] = []
missing_authors:List[str] = []
missing_pdfs:List[str] = []
missing_texts:List[str] = []



# Accessing DOI, PDF, and Text
def get_counts(issue_data):
    for issue in issue_data:
        articles = issue.get('articles', [])
        for article in articles:
            # get info
            doi = get_doi(article)
            author = get_author(article)
            pdf = get_pdf(article)
            text = get_text(article)
            # collect it
            if doi != "":
                dois.append(doi)
            else:
                missing_dois.append(f"vol={issue['volume']} issue={issue['issue']} doi={doi}")
            if author != "":
                authors.append(author)
            else:
                missing_authors.append(f"vol={issue['volume']} issue={issue['issue']} doi={doi}")
            if pdf != "":
                pdfs.append(pdf)
            else:
                missing_pdfs.append(f"vol={issue['volume']} issue={issue['issue']} doi={doi}")
            if text != "":
                texts.append(text)
            else:
                missing_texts.append(f"vol={issue['volume']} issue={issue['issue']} doi={doi}")
    print(f"DOI: {len(dois)}, Authors: {len(authors)}, PDF: {len(pdfs)}, Text: {len(texts)}")

# For article with DoI Updating, PDF, Author, and Text
def update_info(existing_doi_value, new_author_value, new_pdf_value, new_text_value):
    for issue in issue_data:
        articles = issue.get('articles', [])
        for article in articles:
            if existing_doi_value == get_doi(article):
                update_author(article, 'new_author_value')
                update_pdf(article, 'new_pdf_value')
                update_text(article, 'new_text_value')
                print(f"Updated article with {existing_doi_value}.")
                return article
    print(f"No article matching doi {existing_doi_value}")
    return None

def update_issue(issue, existing_doi_value,
                 new_author_value,
                 new_pdf_value="",
                 new_text_value="",
                 author_update=True,  # by default, only author is updated
                 pdf_update=False,
                 text_update=False,
                 ):
    """Given an issue, update the article with the given doi value with new author,
    pdf, and text values. Only the author is updated by default
    """
    articles = issue.get('articles', [])
    for article in articles:
        if existing_doi_value == get_doi(article):

            if author_update:
                update_author(article, new_author_value)
            if pdf_update:
                update_pdf(article, new_pdf_value)
            if text_update:
                update_text(article, new_text_value)
            print(f"Updated article with {existing_doi_value}.")
            return article


get_counts(issue_data)
print(f"\n # Issues with missing authors: ")
for m in missing_authors:
    print(f"   + {m}")
