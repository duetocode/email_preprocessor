#!/user/bin/env python
# coding=utf-8
import nltk
import os
import re
import sys
import multiprocessing
from multiprocessing import Process, Value, Array, Pool, TimeoutError
from sys import stdout
from os import path
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.probability import FreqDist

corpus = []
stemmer = PorterStemmer()
file_counter = 0
counter = Value('h', 0)

URL_REGEX = r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))'
NUMBER_REGEX = r'\d+'
def load(file):
    with open(file, 'r') as fd:
        return unicode(fd.read(), 'utf-8')

def load_all(target):
    global file_counter, corpus
    if path.isdir(target):
        for file in os.listdir(target):
            load_all(path.join(target, file))
    elif os.path.isfile(target):
        corpus.append(load(target))
        file_counter += 1
        stdout.write('\rfiles loaded...%d' % (file_counter))

def process_text(msg):
    with counter.get_lock():
        counter.value += 1
    temp = re.sub(URL_REGEX, 'httpaddr', msg.lower())
    temp = re.sub(NUMBER_REGEX, 'number', temp)
    return [stemmer.stem(word) for word in nltk.word_tokenize(temp) if word not in stopwords.words('english')]


def vectorize():
    try:
        pool = Pool(processes = multiprocessing.cpu_count() - 1)
        res = pool.map_async(process_text, corpus)
        while True:
            try:
                return res.get(1)
            except TimeoutError:
                stdout.write("\rvectorizing...%d" % (counter.value))
                stdout.flush()
    except KeyboardInterrupt:
        pool.terminate()
    else:
        pool.close()


if __name__ == '__main__':
    load_all("processed")
    stdout.write('\n')
    corpus = vectorize()
    stdout.write('\n')
    fdist = FreqDist()
    for doc in corpus:
        for word in doc:
            fdist[word] += 1

    print('vocab counts: %d' % (len(fdist)))
    with open('vocab.txt', 'w') as vocab:
        for word, frequency in fdist.most_common(len(fdist)):
            vocab.write(word.encode('utf-8'))
            vocab.write('\t')
            vocab.write("%d" % (frequency))
            vocab.write('\n')
        vocab.flush()
    print('saved to vocab.txt')