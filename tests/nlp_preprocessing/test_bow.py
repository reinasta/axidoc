import pytest
from pathlib import Path
from src.nlp_preprocessing import bow

def test_file_paths():
    # Validate bow_vectors.pkl
    bow_vectors_path = Path(bow.bow_vectors_path)
    assert bow_vectors_path.exists(), f"{bow_vectors_path} does not exist."
    assert bow_vectors_path.stat().st_size > 0, f"{bow_vectors_path} is empty."

    # Validate vectorizer.pkl
    vectorizer_path = Path(bow.vectorizer_path)
    assert vectorizer_path.exists(), f"{vectorizer_path} does not exist."
    assert vectorizer_path.stat().st_size > 0, f"{vectorizer_path} is empty."

    # Validate tokenized_docs.pkl
    tokenized_docs_path = Path(bow.tokenized_docs_path)
    assert tokenized_docs_path.exists(), f"{tokenized_docs_path} does not exist."
    assert tokenized_docs_path.stat().st_size > 0, f"{tokenized_docs_path} is empty."

    # Validate the directory containing tokenized documents
    directory = Path(bow.directory)
    assert directory.is_dir(), f"{directory} directory does not exist."
    assert any(directory.iterdir()), f"{directory} directory is empty."

