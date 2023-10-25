import os
import re
import spacy
import pandas as pd
import numpy as np
import pickle
from dotenv import load_dotenv

from typing import NamedTuple, Generator, List, Dict, Tuple
from typing import Optional, Any

from load_utils import tokenize_from_file, tokenize_string

# requires
from src.logconf import get_logger
logger = get_logger(__name__)
logger.info("Logging from the axidoc.constants module.")

# Load environment variables from .env file
load_dotenv()
glove_model = os.getenv("MODEL_GLOVE_PRUNED_500K")

nlp = spacy.load(glove_model)

def clean_text(text: str) -> str:
    """Removes newlines and extra spaces from the text."""
    cleaned_text = re.sub(' +', ' ', text.replace('\n', ' '))
    return cleaned_text

def read_text_from_file(file_path: str) -> str:
    """Reads text from a specified file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# objectivity values
objectivity_file = "data/objectivity.txt"
objectivity_text = clean_text(read_text_from_file(objectivity_file))
objectivity_tokenized = tokenize_string(nlp, objectivity_text)

# values in general
values_file = "data/values.txt"
values_text = clean_text(read_text_from_file(values_file))
values_tokenized = tokenize_string(nlp, values_text)

