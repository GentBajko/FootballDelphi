import os

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split as tts

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
dataset = pd.read_excel(os.path.join(__location__, 'dataset.xlsx'), sheet_name='Dataset')

X = dataset[['Home Average', 'Away Average',
             'AVG Conceded Home', 'AVG Conceded Away', 'Over 0.5', 'Under 0.5',
             'Over 1.5', 'Under 1.5', 'Over 2.5', 'Under 2.5', 'BTTS', 'BTTS No',
             'Home Score', 'Away Score']]
y = dataset['Result']

X_train, X_test, y_train, y_test = tts(X, y, random_state=1, test_size=0.20)

random_forest = RandomForestClassifier(n_estimators=30, max_depth=10, random_state=1000)
random_forest.fit(X_train, y_train)

y_pred = random_forest.predict(X_test)

print(X.head())

print(accuracy_score(y_test, y_pred))

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
