from pathlib import Path
from typing import Optional, NamedTuple, List, Dict, Any

# File variables

JSON_ISSUE_FILE:str = "data/issue_data.json"
JSON_UPDATE_FILE:str = "data/issue_data_output.json"
IPS_FILE:str = "data/ip_addresses.txt"
DOILIST_FILE: str = "data/doilist.txt"
DOI_EXCEPTIONS_FILE:str = 'logs/exceptions_doi.txt'
DOWNLOAD_DIR = Path("psychometrika") / "pdf"
DOWNLOAD_DIR_TEXT = Path("psychometrika") / "txt"
