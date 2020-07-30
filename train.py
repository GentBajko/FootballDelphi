from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split as tts
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pandas as pd
import numpy as np


class Train:

    def __init__(self):
        self.data = pd.read_csv('data/dataset.csv').dropna()
        self.x = self.data.drop(['homeTeamFt', 'awayTeamFt', 'homeTeamHt', 'awayTeamHt',
                                 'winner', 'date', 'homeTeam', 'awayTeam'], axis=1)
        self.x_t = pd.read_csv('data/test.csv').drop(['homeTeamFt', 'awayTeamFt ', 'homeTeamHt', 'awayTeamHt',
                                                      'winner', 'date', 'homeTeam', 'awayTeam'], axis=1)
        self.y_t = pd.read_csv('data/test.csv')['winner']
        self.y = self.data['winner']
        self.x_train, self.y_train, _, _ = tts(self.x, self.y, train_size=1, random_state=100)
        self.x_test, self.y_test, _, _ = tts(self.x_t, self.y_t, train_size=1, random_state=100)

    def randomforest(self):
        random_forest = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=1)
        random_forest.fit(self.x_train, self.y_train)

        y_pred = random_forest.predict(self.x_test)

        print(accuracy_score(self.y_test, y_pred))

        print(confusion_matrix(self.y_test, y_pred))
        print(classification_report(self.y_test, y_pred))
        pd.DataFrame({'Result': self.y_test, 'Pred': y_pred}).to_csv('test rf.csv')

    def svm(self):
        pass

    def gnb(self):
        pass


if __name__ == "__main__":
    RandomForest = Train()
    RandomForest.randomforest()
