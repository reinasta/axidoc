import os
import spacy
import logging
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from typing import NamedTuple, Generator, List, Dict, Tuple
from typing import Optional, Any

# requires
from src.logconf import get_logger
logger = get_logger(__name__)
logger.info("Logging from the nlp_preprocessing/bow module.")


# Data

# store data in these pickle files
bow_vectors_path: str = "data/bow_vectors.pkl"
vectorizer_path: str = "data/vectorizer.pkl"
tokenized_docs_path: str = "data/tokenized_docs.pkl"
# Pre-processing

# Step 1: Preprocessing and tokenization
nlp = spacy.load("en_core_web_lg")

# Preprocess and tokenize the documents
tokenized_documents = []
directory = "data/psychometrika/txt"

tokenizer_counter: int = 0  # count successfully tokenized files


# Assuming logger is configured somewhere else
#logger = logging.getLogger(__name__)

def load_saved_data(bow_vectors_path, vectorizer_path, tokenized_docs_path):
    with open(bow_vectors_path, "rb") as file:
        bow_vectors = pickle.load(file)
    with open(vectorizer_path, "rb") as file:
        vectorizer = pickle.load(file)
    with open(tokenized_docs_path, "rb") as file:
        tokenized_documents = pickle.load(file)
    return bow_vectors, vectorizer, tokenized_documents


def build_from_scratch(directory):
    tokenized_documents = []
    for idx, filename in enumerate(os.listdir(directory)):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                try:
                    document_text = file.read()
                except:
                    logger.error(f"Failed to read file {filename}")
                    continue
                try:
                    doc = nlp(document_text)
                    tokens = [
                        token.text.lower()
                        for token in doc
                        if not token.is_stop and token.is_alpha and len(token) > 3
                    ]
                    tokenized_documents.append(" ".join(tokens))
                except:
                    logger.error(f"Failed tokenizing file {filename}")
                    continue

    vectorizer = CountVectorizer()
    try:
        vectorizer.fit(tokenized_documents)
    except:
        logger.error("Failed to vectorize the documents")

    try:
        bow_vectors = vectorizer.transform(tokenized_documents)
    except:
        logger.error("Building bow vectors failed")

    return bow_vectors, vectorizer, tokenized_documents


def save_data(
    bow_vectors,
    vectorizer,
    tokenized_documents,
    bow_vectors_path,
    vectorizer_path,
    tokenized_docs_path,
):
    with open(bow_vectors_path, "wb") as file:
        pickle.dump(bow_vectors, file)
    with open(vectorizer_path, "wb") as file:
        pickle.dump(vectorizer, file)
    with open(tokenized_docs_path, "wb") as file:
        pickle.dump(tokenized_documents, file)


if (
    os.path.isfile(bow_vectors_path)
    and os.path.isfile(vectorizer_path)
    and os.path.isfile(tokenized_docs_path)
):
    logger.info("Loading saved data.")
    bow_vectors, vectorizer, tokenized_documents = load_saved_data(
        bow_vectors_path, vectorizer_path, tokenized_docs_path
    )
else:
    logger.info("Building data from scratch.")
    bow_vectors, vectorizer, tokenized_documents = build_from_scratch(directory)
    save_data(
        bow_vectors,
        vectorizer,
        tokenized_documents,
        bow_vectors_path,
        vectorizer_path,
        tokenized_docs_path,
    )


def get_top_tokens(vectorizer, bow_vectors, top_n=5, num_docs=7):
    """Get the top n tokens for the first num_docs documents."""
    top_tokens = []
    feature_names = vectorizer.get_feature_names_out()
    
    for doc_vector in bow_vectors[0:num_docs]:
        # Get the indices of the highest-weighted features
        top_indices = np.argsort(doc_vector.toarray().flatten())[::-1][:top_n]
        # Get the corresponding tokens
        top_tokens.append([feature_names[idx] for idx in top_indices])
        
    return top_tokens

def compute_similarity(bow_vectors, doc1_index, doc2_index):
    """Compute the similarity between two documents."""
    doc1_vector = bow_vectors[doc1_index]
    doc2_vector = bow_vectors[doc2_index]
    
    similarity_score = cosine_similarity(doc1_vector, doc2_vector)
    
    return similarity_score[0][0]

# Plotting

# logger.info(f"Plotting the similarity between documents.")
## Convert bow_vectors to a DataFrame
# df = pd.DataFrame(bow_vectors.toarray())
## Step 7: Visualize the documents
# plt.figure(figsize=(10, 8))
# sns.scatterplot(data=df, x=0, y=1)
# plt.title("Document Visualization")
# plt.xlabel("Dimension 1")
# plt.ylabel("Dimension 2")
# plt.show()


def load_tokenized_documents(tokenized_docs_path):
    """Load tokenized documents from a pickle file."""
    with open(tokenized_docs_path, 'rb') as file:
        return pickle.load(file)

def tokenize_new_document(nlp, objectivity_file):
    """Tokenizes a new document and returns a tokenized string."""
    with open(objectivity_file, "r", encoding="utf-8") as file:
        objectivity_text = file.read()
    objectivity_tokens = [
        token.text.lower()
        for token in nlp(objectivity_text)
        if not token.is_stop and token.is_alpha and len(token) > 3
    ]
    return " ".join(objectivity_tokens)

def find_similar_documents(vectorizer, bow_vectors, values_tokenized, top_n=10):
    """Finds and returns indices of top_n most similar documents."""
    values_vector = vectorizer.transform([values_tokenized])
    values_similarity_scores = cosine_similarity(values_vector, bow_vectors)
    most_similar_indices = values_similarity_scores.argsort()[0][::-1][:top_n]
    return most_similar_indices

def get_important_tokens(vectorizer, bow_vectors, most_similar_indices, top_n=20):
    """Returns the most important tokens for each similar document."""
    important_tokens_per_document = []
    for doc_vector in bow_vectors[most_similar_indices]:
        sorted_indices = np.argsort(doc_vector.toarray(), axis=1)[:, ::-1]
        important_tokens = [vectorizer.get_feature_names_out()[idx] for idx in sorted_indices[:, :top_n]]
        important_tokens_per_document.append(important_tokens)
    return important_tokens_per_document


def compute_semantic_similarity(doc1, doc2, nlp):
    """Compute the semantic similarity between two documents using word vectors.
    
    It obtains an average vector representation for the two documents and then computes 
    the cosine similarity between these vectors
    
    Parameters:
        doc1, doc2: The texts of the two documents
        nlp: SpaCy model with loaded word vectors
    
    Returns:
        similarity_score: The cosine similarity score between the vectors of the documents
    """
 
    doc1 = nlp(doc1)
    doc2 = nlp(doc2)
    
    doc1_vector = np.array([token.vector for token in doc1 if token.has_vector])
    doc2_vector = np.array([token.vector for token in doc2 if token.has_vector])
    
    if doc1_vector.size == 0 or doc2_vector.size == 0:
        return 0  # return similarity as zero if no vectors found
    
    doc1_vector = np.mean(doc1_vector, axis=0)
    doc2_vector = np.mean(doc2_vector, axis=0)
    
    if np.isnan(doc1_vector).any() or np.isnan(doc2_vector).any():
        return 0  # return similarity as zero if any NaN values are found
    
    similarity_score = cosine_similarity([doc1_vector], [doc2_vector])[0][0]
    return similarity_score

# objectivity values
objectivity_file = "data/objectivity.txt"
objectivity_tokenized = tokenize_new_document(nlp, objectivity_file)

# values in general
values_file = "data/values.txt"
values_tokenized = tokenize_new_document(nlp, values_file)

# tokenized_docs_path: str = "data/tokenized_docs.pkl"

def analyze_objectivity_in_documents(vectorizer, tokenized_docs_path):
    """Performs all the steps to analyze objectivity in a set of documents."""
    # Load tokenized documents from pickle
    tokenized_docs = load_tokenized_documents(tokenized_docs_path)
    
    # Convert the list of tokenized documents to BoW vectors
    bow_vectors = vectorizer.transform(tokenized_docs)
    
    most_similar_indices = find_similar_documents(vectorizer, bow_vectors, objectivity_tokenized)
    
    important_tokens_per_document = get_important_tokens(vectorizer, bow_vectors, most_similar_indices)

    for i, important_tokens in enumerate(important_tokens_per_document):
        print(f"Most important tokens for similar document {i+1} [objectivity terms]:")
        for token in important_tokens:
            print(token)
        print()

def analyze_values_in_documents(vectorizer, tokenized_docs_path, nlp):
    tokenized_docs = load_tokenized_documents(tokenized_docs_path)
    bow_vectors = vectorizer.transform(tokenized_docs)
    most_similar_indices = find_similar_documents(vectorizer, bow_vectors, values_tokenized)
    
    # Integrate semantic similarity comparison
    semantic_scores = []
    for doc in tokenized_docs:
        semantic_scores.append(compute_semantic_similarity(values_tokenized, doc, nlp))
    most_similar_indices_semantic = np.argsort(semantic_scores)[::-1][:10]
    
    # Get important tokens
    important_tokens_bow = get_important_tokens(vectorizer, bow_vectors, most_similar_indices)
    important_tokens_semantic = get_important_tokens(vectorizer, bow_vectors, most_similar_indices_semantic)
    
    return important_tokens_bow, important_tokens_semantic

if __name__ == "__main__":
    important_tokens_bow, important_tokens_semantic = analyze_values_in_documents(vectorizer, tokenized_docs_path, nlp)
    
    logger.info("Most important tokens based on BoW:")
    for i, tokens in enumerate(important_tokens_bow):
        logger.info(f"Document {i+1}: {tokens}")
        
    logger.info("Most important tokens based on Semantic Similarity:")
    for i, tokens in enumerate(important_tokens_semantic):
        logger.info(f"Document {i+1}: {tokens}")
