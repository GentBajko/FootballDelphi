import pandas as pd
from sklearn.model_selection import train_test_split as tts
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
dataset = pd.read_excel(os.path.join(__location__, 'data.xlsx'), sheet_name='Dataset')

dataset = dataset.tail(2000)

X = dataset.drop('Result', axis=1)
y = dataset['Result']

X_train, X_test, y_train, y_test = tts(X, y, test_size = 0.20)

svclassifier = SVC(kernel='linear', C=1.0)
svclassifier.fit(X_train, y_train)

y_pred = svclassifier.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
