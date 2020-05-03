from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split as tts
import pandas as pd
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
dataset = pd.read_excel(os.path.join(__location__, 'dataset.xlsx'), sheet_name='Dataset')

X = dataset.drop('Result', axis=1)
y = dataset['Result']

X_train, X_test, y_train, y_test = tts(X, y, random_state=1, test_size=0.20)

random_forest = RandomForestClassifier(n_estimators=30, max_depth=10, random_state=1000)
random_forest.fit(X_train, y_train)

y_pred = random_forest.predict(X_test)

for x, y in zip(y_test, y_pred):
    print(x == y, x, y, sep=' - ')
print(accuracy_score(y_test, y_pred))

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
