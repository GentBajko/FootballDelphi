import os
from time import perf_counter

import pandas as pd

from api import competitions, API

dataset_start = perf_counter()


class Dataset:

    def __init__(self, objects=None):
        self.objects = competitions if objects is None else objects
        self.championships = {league: API(league).export().data for league in self.objects.keys()}
        self.data = pd.concat(
            [self.championships[df] for df in self.championships],
            join="outer", ignore_index=True).drop_duplicates()
        self.data['winner'] = self.data['winner'].map({'HOME_TEAM': 1, 'AWAY_TEAM': 2, 'DRAW': 3})
        self.data['duration'] = self.data['duration'].map({'REGULAR': 1, 'PENALTY_SHOOTOUT': 2})

    def view_dataset(self):
        print(self.data)
        return self

    def export_dataset(self):
        # TODO: Read file and concat to + remove duplicates
        if 'dataset.csv' in os.listdir(os.path.join(os.getcwd(), 'data')):
            df = pd.read_csv('data/dataset.csv')
            self.data = pd.concat([self.data,
                                   df]).drop_duplicates()
        self.data.to_csv('data/dataset.csv', index=False)
        return self

    def to_postgres(self):
        pass



dataset = Dataset()

if __name__ == "__main__":
    dataset.export_dataset()
    # stats.averages().export()
    print(f"Created dataset in {round(perf_counter() - dataset_start, 2)} seconds")
