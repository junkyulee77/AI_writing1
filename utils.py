
import os
import gzip
import pickle
import random



def save_data(obj, filename):
    file = gzip.GzipFile(filename, 'wb')
    pickle.dump(obj, file)



def load_data(filename):
    file = gzip.GzipFile(filename, 'rb')
    obj = pickle.load(file)
    return obj



def randomChoice(list):
    if len(list) == 0:
        return
    return list[random.randint(0, len(list) - 1)]

