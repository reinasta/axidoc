import subprocess
import gensim.downloader as api
import logging
from typing import List, Optional
import spacy
from spacy.tokens import Doc, Token


from src.logconf import get_logger

# logging
logger = get_logger(__name__)
logger.info("Logging from src/axidoc/load_utils.py module.")



def download_gensim_model(model_name):
    # Download the model using Gensim
    model = api.load(model_name)
    # Save the model to a text file
    model_file_path = f'/path/to/{model_name}.txt'
    model.save_word2vec_format(model_file_path, binary=False)
    return model_file_path

def convert_to_spacy(model_file_path, spacy_model_path):
    # Convert the model to SpaCy format using the command-line utility
    command = f'python -m spacy init vectors en {model_file_path} {spacy_model_path}'
    process = subprocess.run(command, shell=True, check=True)
    if process.returncode != 0:
        logging.error('Failed to convert model to SpaCy format')
        return None
    return spacy_model_path

def download_and_convert(model_name, spacy_model_path):
    """
    Downloads a Gensim model, converts it to a SpaCy model, and saves the SpaCy model to disk.
    
    Parameters:
    model_name (str): The name of the Gensim model to download.
    spacy_model_path (str): The path where the SpaCy model should be saved.
    
    Returns:
    str: The path of the saved SpaCy model, or None if the conversion failed.
    """
    model_file_path = download_gensim_model(model_name)
    if model_file_path:
        spacy_model_path = convert_to_spacy(model_file_path, spacy_model_path)
    return spacy_model_path


def prune_spacy_model(input_model_path, output_model_path, n_vectors):
    # Load the SpaCy model
    nlp = spacy.load(input_model_path)
    # Prune the vectors
    removed_words = nlp.vocab.prune_vectors(n_vectors)
    # Save the pruned model to disk
    nlp.to_disk(output_model_path)
    return output_model_path, removed_words

def prune_model(input_model_path, output_model_path, n_vectors):
    """
    Prunes a SpaCy model to retain only a specified number of vectors, and saves the pruned model to disk.
    
    Parameters:
    input_model_path (str): The path of the input SpaCy model.
    output_model_path (str): The path where the pruned SpaCy model should be saved.
    n_vectors (int): The number of vectors to retain in the pruned model.
    
    Returns:
    tuple: A tuple containing the path of the pruned model and a dictionary of removed words.
    """
    return prune_spacy_model(input_model_path, output_model_path, n_vectors)

def tokenize_string(nlp: spacy.language.Language, text: str) -> List[str]:
    """
    Tokenizes a given string using a specified SpaCy NLP pipeline.

    Parameters:
    - nlp (spacy.language.Language): The SpaCy NLP pipeline to use for tokenization.
    - text (str): The text to be tokenized.

    Returns:
    - List[str]: A list of tokenized words.
    """
    tokens = [
        token.text.lower()
        for token in nlp(text)
        if not token.is_stop and token.is_alpha and len(token) > 3
    ]
    return tokens

def tokenize_from_file(nlp: spacy.language.Language, file_path: str) -> List[str]:
    """
    Reads text from a specified file, and tokenizes it using a specified SpaCy NLP pipeline.

    Parameters:
    - nlp (spacy.language.Language): The SpaCy NLP pipeline to use for tokenization.
    - file_path (str): The path to the file to be read and tokenized.

    Returns:
    - List[str]: A list of tokenized words.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return tokenize_string(nlp, text)

# Usage example:
# Assuming `nlp` is a SpaCy NLP pipeline and `file_path` is the path to a file
# tokens = tokenize_from_file(nlp, file_path)


def string_to_doc(
    nlp: spacy.language.Language, 
    text: str, 
    filters: Optional[List[str]] = None
) -> Doc:
    """
    Tokenizes a given string using a specified SpaCy NLP pipeline.

    Parameters:
    - nlp (spacy.language.Language): The SpaCy NLP pipeline to use for tokenization.
    - text (str): The text to be tokenized.
    - filters (Optional[List[str]]): A list of filters to apply. Supported filters: 'stopwords', 'short_tokens'.

    Returns:
    - Doc: A SpaCy Doc object with the tokenized text, optionally filtered.
    """
    doc = nlp(text)
    filtered_tokens = []

    for token in doc:
        if filters:
            if 'stopwords' in filters and token.is_stop:
                continue
            if 'short_tokens' in filters and len(token) <= 3:
                continue
        filtered_tokens.append(token)

    # Create a new Doc object with filtered tokens while preserving the original Doc's vocab
    filtered_doc = Doc(doc.vocab, words=[token.text for token in filtered_tokens])

    # Log the tokenization and filtering process
    logger.info(f"Tokenized and filtered text: {filtered_doc.text}")
    
    return filtered_doc

# Usage:
# nlp = spacy.load('en_core_web_sm')
# tokenized_doc = tokenize_string(nlp, "Your text here", filters=['stopwords', 'short_tokens'])
