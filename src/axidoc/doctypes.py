import numpy as np
from typing import Callable, NamedTuple, Tuple, Union
from typing import NamedTuple, List, Optional, Any
from spacy.tokens import Doc
from spacy.tokens import Token

from src.logconf import get_logger

# logging
logger = get_logger(__name__)
logger.info("Logging from src/axidoc/doctypes.py module.")

ArrRepresentations = Tuple[Union[np.ndarray, None], Union[np.ndarray, None], Union[np.ndarray, None]]
#SimilarityScores = Tuple[Union[np.ndarray, None], Union[np.ndarray, None], Union[np.ndarray, None]]
SimilarityScores = Tuple[Union[float, None], Union[float, None], Union[float, None]]


class Window(NamedTuple):
    """
    Contains information about a specific window in a document.

    Attributes:
        tokens: List of tokens in the window.
        start_pos: Start position of the window in the document.
        end_pos: End position of the window in the document.
    """

    content: Doc
    start_pos: int
    end_pos: int


class WindowRepresentation(NamedTuple):
    """
    Contains a numerical representation about a specific window in a document.

    Attributes:
        arr: Numerical representation of the window.
        pos: Start and end positions of window onto the document.
    """

    arr: np.ndarray
    pos: Optional[Tuple]
    similarity_score: float = None


class SimRepresentation(NamedTuple):
    """
    Contains numerical representation and similarity scores for a document.

    Attributes:
        doc_representation: Numerical representation of the entire document.
        #features: Optional list of features (tokens) in the document.
        #comparison_features: Optional list of features (tokens) used for comparison.
        comparison_array: Numerical array used for comparison.
        window_repr: Optional list of WindowInfo objects, representing various windows in the document.
        name: Optional string descripting the type of the representation used to compare the documents
    """

    doc_representation: np.ndarray
    #features: Optional[list] = None
    #comparison_features: Optional[list] = None
    comparison_array: Optional[np.ndarray] = None
    window_repr: Optional[List[WindowRepresentation]] = None
    name: Optional[str] = None


class WindowProp(NamedTuple):
    window_size: Optional[int] = None
    window_overlap: Optional[int] = None
    window_shift: Optional[int] = None
    window_type: Optional[str] = None  # 'sentence', 'paragraph', 'document'

class DocumentWrapper(NamedTuple):
    """
    Wraps a SpaCy Doc object and its various numerical representations.

    Attributes:
        doc: Original SpaCy Doc object.
        bow: Bag-of-Words representation and related information.
        word2vec: Word2Vec representation and related information.
        glove: GloVe representation and related information.
    """

    doc: Doc
    bow: Optional[SimRepresentation] = None
    word2vec: Optional[SimRepresentation] = None
    glove: Optional[SimRepresentation] = None
    window_prop: Optional[WindowProp] = None


def sorted_windows_scores(
    document_wrapper: DocumentWrapper, representation_type: Optional[str] = None
) -> DocumentWrapper:
    """Sorts windows in decending order based on their similarity scores.
        document_wrapper: DocumentWrapper instance
        representation_type: Optional[str]: if None (default), all representations are sorted.
            If 'bow', 'word2vec', or 'glove', only the specified representation is sorted.
    """
    def sort_windows(sim_rep: SimRepresentation) -> SimRepresentation:
        sorted_window_repr = sorted(
            sim_rep.window_repr, key=lambda x: x.similarity_score, reverse=True
        )
        return sim_rep._replace(window_repr=sorted_window_repr)

    if representation_type:
        if representation_type not in ["bow", "word2vec", "glove"]:
            raise ValueError(
                "Invalid representation_type. Choose from 'bow', 'word2vec', 'glove'."
            )
        sim_rep = getattr(document_wrapper, representation_type)
        updated_sim_rep = sort_windows(sim_rep)
        document_wrapper = document_wrapper._replace(**{representation_type: updated_sim_rep})
    else:
        for rep_type in ["bow", "word2vec", "glove"]:
            sim_rep = getattr(document_wrapper, rep_type)
            if sim_rep:
                updated_sim_rep = sort_windows(sim_rep)
                document_wrapper = document_wrapper._replace(**{rep_type: updated_sim_rep})

    return document_wrapper

