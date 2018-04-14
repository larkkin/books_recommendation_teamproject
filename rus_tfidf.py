#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from string import punctuation
from nltk import word_tokenize
from nltk.corpus import stopwords
import io
import sys
import os

if len(sys.argv) != 2:
	print("\tusage: ./rus_tfidf.py <books_dir>")
	exit()


nltk.download('stopwords')

stopWords = stopwords.words('russian')+ list(punctuation) + ["«", "»", "—"]

def get_text(path):
    with io.open(path, "r", encoding="UTF8") as infile:
        line = infile.readlines()
        return ''.join(line)

def tokenize(text):
    words = word_tokenize(text)
    words = [w.lower() for w in words]
    return [w for w in words if w not in stopWords and not w.isdigit()]


books_dir = sys.argv[1]
filenames = os.listdir(books_dir)
filenames.sort()
texts = [get_text(books_dir+'/'+name) for name in filenames]
words = [tokenize(l) for l in texts]

vocabulary = set()
for w in words:
	vocabulary.update(w)
vocabulary = list(vocabulary)
vocabulary.sort()
with open("./vocab.dat", 'w') as otp:
	otp.write('\n'.join(vocabulary))
word_index = {w: idx for idx, w in enumerate(vocabulary)}
tfidf = TfidfVectorizer(stop_words=stopWords, tokenizer=tokenize, vocabulary=vocabulary)
tfidf.fit(texts)
X = tfidf.transform(texts)
# for i in vocabulary:
# 	print (X[2, tfidf.vocabulary_[i]], i)

top_10k_words = {}
with open("./mult.dat", 'w') as otp:
	for i in range(len(texts)):
		name = filenames[i]
		current_vocab = set(words[i])
		top_words = [(word_index[w], X[i, tfidf.vocabulary_[w]]) for w in current_vocab]
		top_words.sort(key=lambda x: x[1])
		top_10k_words[name] = top_words[-10000:]
		otp.write("{} ".format(len(words[i])))
		otp.write(' '.join([str(p[0]) + ":" + str(p[1]) for p in top_words]))
		otp.write('\n')


#print(top_10k_words[filenames[0]])

