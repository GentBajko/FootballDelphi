import os
from datetime import datetime, timedelta

import pandas as pd
import requests

competitions = {"Bundesliga": "BL1", "Serie A": "SA", "Premiere League": "PL",
                "England Championship": "ELC",
                "Ligue 1": "FL1", "Eredivisie": "DED",
                "Primiera Liga": "PPL", "Primera Division": "PD"}
# Also "Brazil Serie A": "BSA", "Champions League": "CL",


class API:
    """
    Connection to football-data.org's API.

    For a specific championship:
    championship: One of the keys from the championships list above.
    request: Default value which is "competitions"
    start: Get data from this starting date. Default value is the max value of 755 days
           worth of matches for that championship. Datetime format is "%Y-%m-%d".
    finish: Get data until this date. Default date is whatever the current date is when
            the script is run. Datetime format is "%Y-%m-%d".
    EXAMPLE: Bundesliga = API(request="competitions", champinship="BL1", start="2019-01-01",
                              finish=datetime.today().strftime("%Y-%m-%d")

    For total matches:
    championship: None
    request: "matches"
    start: Default value is the max value of 10 days worth of matches.
           Datetime format is "%Y-%m-%d".
    finish: Default date is whatever the current date is when the script
            is run. Datetime format is "%Y-%m-%d".

    EXAMPLE: All_Matches = API(request="competitions", champinship="BL1",
                               start=datetime.today().strftime("%Y-%m-%d") - timedelta(days=1),
                              finish=datetime.today().strftime("%Y-%m-%d")
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, championship=None, request="competitions",
                 start=(datetime.now() - timedelta(days=755)).strftime("%Y-%m-%d"),
                 finish=datetime.today().strftime("%Y-%m-%d")):
        self.request = request
        self.championship = competitions[championship] if championship is not None else None
        self.start = start if self.request == "competitions" \
            else (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        self.finish = finish if self.request == "competitions" \
            else datetime.today().strftime("%Y-%m-%d")
        self.status = 'FINISHED'
        if not self.start:
            self.url = f'https://api.football-data.org/v2/{self.request}/' \
                       f'{self.championship}/matches?status={self.status}'
        if self.championship is None:
            self.url = f'https://api.football-data.org/v2/{self.request}?status={self.status}&' \
                       f'dateFrom={self.start}&dateTo={self.finish}'
        else:
            self.url = f'https://api.football-data.org/v2/{self.request}/{self.championship}/' \
                       f'matches?status={self.status}&dateFrom={self.start}&dateTo={self.finish}'
        try:
            self.response = requests.get(self.url, headers={
                'X-Auth-Token': '100fd57ea04c4f78b938d532bd9f93ce'}).json()
            print(self.response)
            if self.response['count'] != 0:
                data = pd.json_normalize(self.response["matches"])
                data = data.drop(["referees", "status", "odds.msg",
                                  "season.startDate", "season.endDate", "stage",
                                  "group", "score.extraTime.homeTeam",
                                  "score.extraTime.awayTeam", "lastUpdated",
                                  "score.penalties.homeTeam", "score.penalties.awayTeam"],
                                 axis=1)
                self.data = data.rename(
                    columns={'id': 'matchID', 'utcDate': 'date',
                             'season.currentMatchday': 'matchDay',
                             'score.winner': 'winner', 'score.duration': 'duration',
                             'score.fullTime.homeTeam': 'homeTeamFt',
                             'score.fullTime.awayTeam': 'awayTeamFt',
                             'score.halfTime.homeTeam': 'homeTeamHt',
                             'score.halfTime.awayTeam': 'awayTeamHt',
                             'homeTeam.id': 'homeTeamID', 'awayTeam.id': 'awayTeamID',
                             'homeTeam.name': 'homeTeam', 'awayTeam.name': 'awayTeam'})
                self.data["date"] = self.data["date"].str.replace("Z", "").str.replace("T", " ")
                print(f"Initialized {self.championship} with URL {self.url}")
            else:
                print(f"Error {self.response['errorCode']}: {self.response['message']}"
                      if 'errorCode' in self.response
                      else f"No data for {self.championship}")
        except AttributeError:
            self.data = pd.DataFrame()
            print(f"{self.championship} currently has no data.")

    def __getitem__(self, item):
        return self.data[item]

    def export(self):
        """
        Exports API dataframes into a csv file for later use.
        :return: self
        """
        if "data" not in os.listdir(os.getcwd()):
            os.mkdir("data")
        if self.request == "matches":
            historical = pd.read_csv('data/historical.csv', encoding='utf-8')
            self.data = pd.concat([self.data,
                                  historical], axis=0, ignore_index=True).drop_duplicates()
            self.data.to_csv(f"historical.csv", encoding="utf-8")
        else:
            self.data.to_csv(f"data/{self.championship} "
                             f"{datetime.today().strftime('%Y-%m-%d')}.csv",
                             encoding='utf-8')
        return self


AllMatches = API(request="matches")

if __name__ == "__main__":
    # AllMatches.export()

    Brazil = API(championship='BSA')
    Brazil.export()
