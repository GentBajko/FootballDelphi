import os
from time import perf_counter

import pandas as pd

from api import competitions, API

dataset_start = perf_counter()


class Dataset:

    def __init__(self, objects=None):
        self.objects = competitions if objects is None else objects
        self.championships = {league: API(league).export().data for league in self.objects.keys()}
        self.all_matches = API(request="matches").data
        self.data = pd.concat(
            [self.championships[df] for df in self.championships],
            join="outer").reset_index().drop_duplicates()
        print("Dataset is ready")
        if 'historical.csv' not in os.listdir(os.path.join(os.getcwd(), 'data')):
            pd.DataFrame().to_csv('data/historical.csv', encoding='utf-8')
        self.historical = pd.read_csv('data/historical.csv', encoding='utf-8')

    def view_dataset(self, dataframe: str):
        if dataframe == "championships":
            print(self.data)
        elif dataframe == 'historical':
            print(self.all_matches)
        return self

    def export_dataset(self):
        # TODO: Read file and concat to + remove duplicates
        self.data.to_csv('data/dataset.csv')


dataset = Dataset()

if __name__ == "__main__":

    dataset.view_dataset('championships').export_dataset()

    print(f"Created dataset in {round(perf_counter() - dataset_start, 2)} seconds")
