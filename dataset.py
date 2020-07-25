import os
from time import perf_counter
import pandas as pd
from api import competitions, API


class Dataset:

    def __init__(self, objects: list or str, ):
        os.chdir(os.getcwd())
        self.objects = competitions if objects is not None else objects
        self.championships = [API(league) for _, league in self.objects]
        self.all_matches = API(request="matches").data
        self.data = pd.DataFrame()

    def build_dataset(self):
        self.data = pd.merge([df for df in self.championships], join="outer").drop_duplicates()
        return self

    def view_dataset(self, dataframe: str):
        if dataframe == "championships":
            print(self.data)
        elif dataframe == 'historical':
            print(self.all_matches)
        return self


if __name__ == "__main__":
    FourYearData = Dataset()

    FourYearData.build_dataset().view_dataset('historical')
