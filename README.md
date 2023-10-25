This is a Natural Language Processing (NLP) study of values expressed by 
academic papers[^fn1] published over a couple of decades.
By values we mean terms like 'objectivity', 'accuracy', 'truth', but also 'fairness',
'equality', 'freedom', 'utility' etc.
We are interested in how the values expressed have changed over time.

[^fn1]: We are primarily interested in more formal/mathematical topics, and
start our study by looking at Psychometrics articles. The research can then
be extended to other disciplines and texts.

> Note: this is still in exploratory phase; no tangible results are in as yet.

### Project Plan

#### Phase 1: Data Preparation and Preprocessing
1. **Data Collection Verification**: Validate dataset completeness and relevance.
2. **Text Cleaning**: Utilize stemming, lemmatization, and stopword removal.
3. **Data Splitting**: Partition dataset into training, validation, and test sets.

#### Phase 2: Exploratory Data Analysis (EDA)
1. **Initial Insights**: Analyze basic statistics and metrics.
2. **Value-Term Frequency**: Investigate term frequencies for key value-terms.
3. **Temporal Trends**: Study term frequency over time.

#### Phase 3: Feature Engineering
1. **Bag of Words (BoW)**: Implement as a baseline.
2. **TF-IDF**: Use for term importance.
Word Embeddings: Capture semantic meanings.
3.1 **GloVe Vectors**: Utilize pretrained GloVe vectors for semantic similarity.
3.2 **Word2Vec**: Use pretrained word2vec vectors.
Semantic Similarity: Integrate GloVe vectors or other embeddings into similarity computations.
4.1 **Cosine Similarity with Embeddings**: Compute cosine similarity scores using word embeddings.
4.2 **Document Embedding**: Create document-level embeddings by averaging or weighting word embeddings.
4.3 **Topic Modeling**: Identify key topics.

#### Phase 4: Model Building
1. **Rule-Based Methods**: Implement sentiment capture for value-terms.
2. **Machine Learning Models**: Use Random Forests, XGBoost, Naive Bayes, or SVMs.
3. **Deep Learning Models**: Explore RNNs or Transformers.

#### Phase 5: Evaluation Metrics
1. **Standard Metrics**: Evaluate via accuracy, precision, recall, and F1-score.
2. **Inter-annotator Agreement**: Manually annotate and compare.

#### Phase 6: Deployment and Monitoring
1. **API Creation**: Use Django for deployment.
2. **Monitoring**: Implement logging and performance tracking.
3. **Continuous Updating**: Update model with new academic papers.

#### Optional:
1. **Advanced NLP**: Explore sentiment models or transfer learning.
2. **Explainability**: Use techniques like LIME or SHAP.
3. **Testing and Logging**: Ensure codebase stability and scalability.

### Tech Stack
- **Data Preparation**: Pandas, SpaCy
- **EDA**: Matplotlib, Seaborn
- **Feature Engineering**: Scikit-learn, Gensim, SpaCy
- **Model Building**: Scikit-learn, PyTorch
- **Deployment**: Django


# Activate virtual environment

```bash
conda activate nlpenv
```

You can then install dependencies from a `env.yml`:

```bash
conda create -f env.yml
```


While environment is activate, you can install a package:

```bash
conda install <package-namee> -c conda-forge
```
