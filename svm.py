import os

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split as tts
from sklearn.svm import SVC

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
dataset = pd.read_excel(os.path.join(__location__, 'dataset.xlsx'), sheet_name='Dataset')


X = dataset[['Home Average', 'Away Average',
             'AVG Conceded Home', 'AVG Conceded Away', 'Over 0.5', 'Under 0.5',
             'Over 1.5', 'Under 1.5', 'Over 2.5', 'Under 2.5', 'BTTS', 'BTTS No',
             'Home Score', 'Away Score']]
y = dataset['Result']

X_train, X_test, y_train, y_test = tts(X, y, test_size=0.30)

svclassifier = SVC(kernel='linear', C=1.0)
svclassifier.fit(X_train, y_train)

y_pred = svclassifier.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
