import sys
print(sys.path)


import pytest

from axidoc.doctypes import sorted_windows_scores
from axidoc.repr import text_to_document_wrapper
from axidoc.constants import values_text, objectivity_text
from tests.test_utils import text_with_values, text_wo_values

# Threshold for the second test
SIMILARITY_THRESHOLD = 0.5


def test_creating_a_document_wrapper():
    document_wrapper = text_to_document_wrapper(
        text=text_with_values, comparison_text=values_text,
    )
    assert document_wrapper is not None, "Document wrapper is None"
    assert document_wrapper.bow is not None, "Document wrapper's bow attribute is None"
    assert document_wrapper.word2vec is not None, "Document wrapper's word2vec attribute is None"
    assert document_wrapper.glove is not None, "Document wrapper's glove attribute is None"

def test_max_greater_than_min_for_text_with_values_bow():
    document_wrapper_with_values = text_to_document_wrapper(
        text=text_with_values, comparison_text=values_text,
    )
    
    sorted_doc = sorted_windows_scores(document_wrapper_with_values)
    min_score = sorted_doc.bow.window_repr[-1].similarity_score
    max_score = sorted_doc.bow.window_repr[0].similarity_score
    
    assert max_score > min_score, "Min (BOW) score should be less than the max score"

def test_max_greater_than_min_for_text_with_values_word2vec():
    document_wrapper_with_values = text_to_document_wrapper(
        text=text_with_values, comparison_text=values_text,
    )
    
    sorted_doc = sorted_windows_scores(document_wrapper_with_values)
    min_score = sorted_doc.word2vec.window_repr[-1].similarity_score
    max_score = sorted_doc.word2vec.window_repr[0].similarity_score
    
    assert max_score > min_score, "Min (Word2Vec) score should be less than the max score"

def test_max_greater_than_min_for_text_with_values_glove():
    document_wrapper_with_values = text_to_document_wrapper(
        text=text_with_values, comparison_text=values_text,
    )
    
    sorted_doc = sorted_windows_scores(document_wrapper_with_values)
    min_score = sorted_doc.glove.window_repr[-1].similarity_score
    max_score = sorted_doc.glove.window_repr[0].similarity_score
    
    assert max_score > min_score, "Min (Glove) score should be less than the max score"


def test_max_near_min_for_text_wo_values_bow():
    document_wrapper_wo_values = text_to_document_wrapper(
        text=text_wo_values, comparison_text=values_text,
        )
    
    sorted_doc = sorted_windows_scores(document_wrapper_wo_values)
    min_score = sorted_doc.bow.window_repr[-1].similarity_score
    max_score = sorted_doc.bow.window_repr[0].similarity_score
       
    assert max_score - min_score >= SIMILARITY_THRESHOLD, "Threshold is not met (bow)"


def test_max_near_min_for_text_wo_values_word2vec():
    document_wrapper_wo_values = text_to_document_wrapper(
        text=text_wo_values, comparison_text=values_text,
        )
    
    sorted_doc = sorted_windows_scores(document_wrapper_wo_values)
    min_score = sorted_doc.word2vec.window_repr[-1].similarity_score
    max_score = sorted_doc.word2vec.window_repr[0].similarity_score
       
    assert max_score - min_score >= SIMILARITY_THRESHOLD, "Threshold is not met (word2vec)"


def test_max_near_min_for_text_wo_values_glove():
    document_wrapper_wo_values = text_to_document_wrapper(
        text=text_wo_values, comparison_text=values_text,
        )
    
    sorted_doc = sorted_windows_scores(document_wrapper_wo_values)
    min_score = sorted_doc.glove.window_repr[-1].similarity_score
    max_score = sorted_doc.glove.window_repr[0].similarity_score
       
    assert max_score - min_score >= SIMILARITY_THRESHOLD, "Threshold is not met (glove)"
