import os
import spacy
from spacy.tokens import Doc
import gensim.downloader as api
import numpy as np
from typing import List, Optional, Tuple, Union
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv


from src.logconf import get_logger
from src.axidoc.doctypes import (
    DocumentWrapper, SimRepresentation, WindowProp, ArrRepresentations,
    SimilarityScores, Window, WindowRepresentation
)
from src.axidoc.load_utils import tokenize_string
from src.axidoc.constants import values_text, objectivity_text


# Load environment variables from .env file
load_dotenv()
glove_model = os.getenv("MODEL_GLOVE_PRUNED_500K")  # from .env file
w2v_model = os.getenv("MODEL_W2V_PRUNED_500K")  # from .env file

# logging
logger = get_logger(__name__)
logger.info("Logging from src/axidoc/repr.py module.")

# Load SpaCy model (including pretrained GloVe vectors)
nlp_glove = spacy.load(glove_model)
logger.info("Loaded glove model.")
nlp_w2v = spacy.load(w2v_model)
logger.info("Loaded word2vec model.")


def compute_bow_representation(
    doc: spacy.tokens.Doc, vectorizer: Optional[CountVectorizer] = None
) -> Tuple[np.ndarray, CountVectorizer]:
    text = " ".join([token.text for token in doc])
    if vectorizer is None:
        vectorizer = CountVectorizer()
        vectorizer.fit([text])
    bow_matrix = vectorizer.transform([text])
    return np.array(bow_matrix.toarray()).flatten(), vectorizer


def compute_glove_representation(doc: spacy.tokens.Doc) -> np.ndarray:
    return np.array([token.vector for token in doc])


def compute_word2vec_representation(doc: spacy.tokens.Doc) -> np.ndarray:
    return np.array([token.vector for token in doc])


def compute_similarity(rep1: np.ndarray, rep2: np.ndarray) -> float:
    try:
        # Ensure the inputs are numpy arrays
        assert isinstance(rep1, np.ndarray) and isinstance(rep2, np.ndarray), "Inputs must be numpy arrays"
        
        # Compute and return the cosine similarity
        similarity_score = cosine_similarity([rep1], [rep2])[0][0]
        return similarity_score
    
    except AssertionError as e:
        logger.error(f"Assertion error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"An error occurred while computing similarity: {e}")
        raise

def representation_func(text_or_doc: Union[str, spacy.tokens.Doc], vectorizer: CountVectorizer) -> ArrRepresentations:
    """Vectorizes text according to three different text representation types (BoW, GloVe, Word2Vec)."""
    if isinstance(text_or_doc, str):
        doc_glove = nlp_glove(text_or_doc)
        doc_w2v = nlp_w2v(text_or_doc)
    else:
        doc_glove = text_or_doc
        doc_w2v = text_or_doc
    
    bow_representation, _ = compute_bow_representation(doc_glove, vectorizer)
    glove_representation = compute_glove_representation(doc_glove)
    word2vec_representation = compute_word2vec_representation(doc_w2v)
    
    return bow_representation, glove_representation, word2vec_representation


def similarity_func(
    target_representations: ArrRepresentations,
    comparison_representations: ArrRepresentations
) -> SimilarityScores:
    """Computes similarity scores between two texts using three different text representation types (BoW, GloVe, Word2Vec)."""
    
    if target_representations[0] is None or comparison_representations[0] is None:
        logger.warning("BoW representations are None, similarity cannot be computed.")
        bow_similarity = None
    else:
        bow_similarity = compute_similarity(
            target_representations[0], comparison_representations[0]
        )
    
    if target_representations[1] is None or comparison_representations[1] is None:
        logger.warning("GloVe representations are None, similarity cannot be computed.")
        glove_similarity = None
    else:
        glove_similarity = compute_similarity(
            target_representations[1].mean(axis=0), comparison_representations[1].mean(axis=0)
        )
    
    if target_representations[2] is None or comparison_representations[2] is None:
        logger.warning("Word2Vec representations are None, similarity cannot be computed.")
        word2vec_similarity = None
    else:
        word2vec_similarity = compute_similarity(
            target_representations[2].mean(axis=0), comparison_representations[2].mean(axis=0)
        )
    
    return bow_similarity, glove_similarity, word2vec_similarity

def segment(doc: Doc, window_prop: WindowProp) -> List[Window]:
    windows = []

    try:
        if window_prop.window_type == 'sentence':
            for sent in doc.sents:
                window = Window(content=sent, start_pos=sent.start_char, end_pos=sent.end_char)
                windows.append(window)
        elif window_prop.window_type == 'paragraph':
            start = 0
            for token in doc:
                if token.is_space and token.text.count("\n") > 1:
                    window = Window(content=doc[start:token.i], start_pos=doc[start].idx, end_pos=doc[token.i - 1].idx + len(doc[token.i - 1]))
                    windows.append(window)
                    start = token.i
            window = Window(content=doc[start:], start_pos=doc[start].idx, end_pos=doc[-1].idx + len(doc[-1]))
            windows.append(window)
        else:
            window_size = window_prop.window_size or len(doc)
            window_shift = window_prop.window_shift or window_size
            for start_token_idx in range(0, len(doc), window_shift):
                end_token_idx = min(start_token_idx + window_size, len(doc))
                window = Window(content=doc[start_token_idx:end_token_idx], start_pos=doc[start_token_idx].idx, end_pos=doc[end_token_idx - 1].idx + len(doc[end_token_idx - 1]))
                windows.append(window)
    except Exception as e:
        logger.error(f"Failed to segment document: {e}")
        raise

    logger.info(f"Successfully segmented document into {len(windows)} windows.")
    return windows

def compute_window_representation(
    window: Window, vectorizer: CountVectorizer, comparison_representations: ArrRepresentations
) -> WindowRepresentation:
    window_target_reprs = representation_func(window.content, vectorizer)
    window_similarity_scores = similarity_func(window_target_reprs, comparison_representations)
    return WindowRepresentation(
        arr=window_target_reprs[0],  # Assuming BoW representation here
        pos=(window.start_pos, window.end_pos),
        similarity_score=window_similarity_scores[0]  # Assuming BoW similarity score here
    )
def text_to_document_wrapper(
    text: Union[str, spacy.tokens.Doc], 
    comparison_text: Optional[Union[str, spacy.tokens.Doc]] = None,
    window_prop: WindowProp = WindowProp(window_size=20, window_shift=10)
) -> DocumentWrapper:
    """
    Generates a document wrapper for the given text and optional comparison document.

    Args:
        text (Union[str, spacy.tokens.Doc]): The input text or Doc to generate the document wrapper for.
        comparison_text (Optional[Union[str, spacy.tokens.Doc]]): The comparison text or Doc to compute similarity scores with.
            Defaults to None. If not provided, similarity scores will not be computed.
        window_prop (WindowProp): Window properties for analyzing text segments. Defaults to 
        an empty WindowProp.

    Returns:
        DocumentWrapper: The generated document wrapper.

    Raises:
        ValueError: If no comparison document is provided.
    """

    if text is None or comparison_text is None:
        logger.error("Text or comparison text cannot be None")
        raise ValueError("Text or comparison text cannot be None")

    # Adapt vectorizer fitting
    text_content = text.text if isinstance(text, spacy.tokens.Doc) else text
    comparison_text_content = (
        comparison_text.text if isinstance(comparison_text, spacy.tokens.Doc) else comparison_text
    )
    vectorizer = CountVectorizer()
    vectorizer.fit([text_content, comparison_text_content])

    # Retrieve representations
    target_representations = representation_func(text, vectorizer)
    comparison_representations = representation_func(comparison_text, vectorizer)

    # Compute similarities
    similarities = similarity_func(target_representations, comparison_representations)

    # Build SimRepresentation instances
    sim_reprs = {
        rep_type: SimRepresentation(
            doc_representation=target_representations[i],
            #features=vectorizer.get_feature_names(),
            comparison_array=comparison_representations[i],
            name=rep_type,
        )
        for i, rep_type in enumerate(["bow", "glove", "word2vec"])
    }

    # Check for None window_prop and log a warning if necessary
    if window_prop is None or all(value is None for value in window_prop._asdict().values()):
        logger.warning(
            "No segmentation will be performed, the entire document will be used as a single window."
        )
        #windows = [Window(content=text, start_pos=0, end_pos=len(text_content))]
        windows = [
            WindowRepresentation(
                arr=target_representations[i],
                pos=(0, len(text_content)),
                similarity_score=similarities[i])
                for i, rep_type in enumerate(["bow", "glove", "word2vec"])
            ]
    else:
        # Segment the text
        doc = nlp_glove(text_content)  # Ensure we have a Doc object
        windows = segment(doc, window_prop)

    # For each window, compute its representations and similarity scores
    window_reprs = {'bow': [], 'glove': [], 'word2vec': []}
    for window in windows:
        window_target_reprs = representation_func(window.content, vectorizer)
        window_similarity_scores = similarity_func(window_target_reprs, comparison_representations)
        for i, rep_type in enumerate(["bow", "glove", "word2vec"]):
            window_repr = WindowRepresentation(
                arr=window_target_reprs[i],
                pos=[window.start_pos, window.end_pos],
                similarity_score=window_similarity_scores[i]
            )
            window_reprs[rep_type].append(window_repr)

    # Create the DocumentWrapper instance
    document_wrapper = DocumentWrapper(
        doc=doc,
        bow=SimRepresentation(
            doc_representation=target_representations[0],
            window_repr=window_reprs['bow'],
            name="bow"
        ),
        word2vec=SimRepresentation(
            doc_representation=target_representations[2],
            window_repr=window_reprs['word2vec'],
            name="word2vec"
        ),
        glove=SimRepresentation(
            doc_representation=target_representations[1],
            window_repr=window_reprs['glove'],
            name="glove"
        ),
        window_prop=window_prop
    )

    return document_wrapper

