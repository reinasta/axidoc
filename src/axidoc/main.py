import spacy
import en_core_web_sm
import en_core_web_lg

nlp = spacy.load("en_core_web_sm")
nlp = en_core_web_sm.load()

# setence tokens
sent = "This is a sentence."
doc = nlp(sent)
print('\n' + sent)
print([(w.text, w.pos_) for w in doc])

# setence 1 tokens
sent_1 = "Apple is looking at buying U.K. startup for $1 billion."
doc_1 = nlp(sent_1)
print('\n' + sent_1)
for token in doc_1:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)

print('\n' + 'Named entities')
for ent in doc_1.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)

# setence 2 vectors
sent_2 = "dog cat banana afskfsd"
nlp_lg = spacy.load("en_core_web_lg")  # load large pipeline (with word-vectors)
doc_2 = nlp_lg(sent_2)

print('\n' + 'Word vectors')
for token in doc_2:
    print(token.text, token.has_vector, token.vector_norm, token.is_oov)

# sentence similarity
doc_3 = nlp_lg("I like salty fries and hamburgers.")
doc_4 = nlp_lg("Fast food tastes very good.")

# Similarity of two documents
print('\n' + 'Similarity of documents and spans')
print(doc_3, "<->", doc_4, doc_3.similarity(doc_4))
# Similarity of tokens and spans
french_fries = doc_3[2:4]
burgers = doc_3[5]
print(french_fries, "<->", burgers, french_fries.similarity(burgers))
