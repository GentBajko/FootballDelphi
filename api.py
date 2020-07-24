import requests
import pandas as pd
import os
from time import strptime


class API:

    # pylint: disable=too-many-instance-attributes

    def __init__(self, request: str, championship: str, start=None, finish=None, status='FINISHED'):
        self.request = request
        self.championship = championship
        self.start = start
        self.finish = finish
        self.status = status
        if not start:
            self.url = f'https://api.football-data.org/v2/{self.request}/' \
                       f'{self.championship}/matches?status={self.status}'
        else:
            self.url = f'https://api.football-data.org/v2/{self.request}/{self.championship}/' \
                       f'matches?status={self.status}&dateFrom={self.start}&dateTo={self.finish}'
        self.response = requests.get(self.url, headers={
            'X-Auth-Token': '100fd57ea04c4f78b938d532bd9f93ce'}).json()
        self.data = pd.json_normalize(self.response["matches"])
        self.data = self.data.drop(["referees", "status", "odds.msg", "season.startDate", "season.endDate", "stage",
                                    "group", "score.extraTime.homeTeam", "score.extraTime.awayTeam", "lastUpdated",
                                    "score.penalties.homeTeam", "score.penalties.awayTeam"],
                                   axis=1)
        self.data = self.data.rename(columns={'id': 'matchID', 'utcDate': 'date', 'season.currentMatchday': 'matchDay',
                                              'score.winner': 'winner', 'score.duration': 'duration',
                                              'score.fullTime.homeTeam': 'homeTeamFt',
                                              'score.fullTime.awayTeam': 'awayTeamFt',
                                              'score.halfTime.homeTeam': 'homeTeamHt',
                                              'score.halfTime.awayTeam': 'awayTeamHt',
                                              'homeTeam.id': 'homeTeamID', 'awayTeam.id': 'awayTeamID',
                                              'homeTeam.name': 'homeTeam', 'awayTeam.name': 'awayTeam'})

    def __getitem__(self, item):
        return self.data[item]

    def export(self):
        print(os.getcwd())
        if "data" not in os.listdir(os.getcwd()):
            os.mkdir("data")
        self.data.to_csv(f"data/{self.championship}.csv")
        return self

    def rename_cols(self):
        self.data = self.data.rename(columns={'id': 'matchID', 'utcDate': 'date', 'season.currentMatchday': 'matchDay',
                                              'score.winner': 'winner', 'score.duration': 'duration',
                                              'score.fullTime.homeTeam': 'homeTeamFt',
                                              'score.fullTime.awayTeam': 'awayTeamFt',
                                              'score.halfTime.homeTeam': 'homeTeamHt',
                                              'score.halfTime.awayTeam': 'awayTeamHt',
                                              'homeTeam.id': 'homeTeamID', 'awayTeam.id': 'awayTeamID',
                                              'homeTeam.name': 'homeTeam', 'awayTeam.name': 'awayTeam'})
        return self

    def fix_dates(self):
        self.data = self.data['date'].replace('T', ' ').replace('Z', '')
        return self


if __name__ == "__main__":
    SerieA = API(request="competitions", championship="SA")
    Bundesliga = API(request="competitions", championship="BL1")
    print(Bundesliga.data)
    print(pd.merge([SerieA.data, Bundesliga.data], join="outer"))
    SerieA.fix_dates()
    print(SerieA['date'].apply(lambda date: strptime(date, '%Y-%m-%d %H')))
