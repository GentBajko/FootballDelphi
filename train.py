from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split as tts
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np


class Train:

    def __init__(self, data):
        self.data = pd.read_csv('data/dataset.csv')

    def randomforest(self):
        pass

    def svm(self):
        pass

    def gnb(self):
        pass