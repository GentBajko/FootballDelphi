from scipy.stats import poisson
import pandas as pd
import numpy as np
from time import perf_counter

start_stats = perf_counter()


class Stats:

    # TODO: Poisson Distribution conceeded. Maybe (Pmf Avg + Pmf Cond) / 2

    def __init__(self):
        self.data = pd.read_csv('data/dataset.csv', index_col=0).dropna()

    def averages(self):
        """
        Calculates the expaning mean for each match and selects the one with the matching
        index for that specific match.
        """
        # Fulltime Home
        self.data['homeAverageFt'] = [round(
            self.data[
                self.data['homeTeam'] == team]['homeTeamFt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['homeTeam'], self.data['homeTeam'].index)]
        self.data['homeConcededFt'] = [round(
            self.data[
                self.data['homeTeam'] == team]['awayTeamFt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['homeTeam'], self.data['homeTeam'].index)]
        # Halftime Home
        self.data['homeAverageHt'] = [round(
            self.data[
                self.data['homeTeam'] == team]['homeTeamHt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['homeTeam'], self.data['homeTeam'].index)]
        self.data['homeConcededHt'] = [round(
            self.data[
                self.data['homeTeam'] == team]['awayTeamHt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['homeTeam'], self.data['homeTeam'].index)]
        # Fulltime Away
        self.data['awayAverageFt'] = [round(
            self.data[
                self.data['awayTeam'] == team]
            ['awayTeamFt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['awayTeam'], self.data['awayTeam'].index)]
        self.data['awayConcededFt'] = [round(
            self.data[
                self.data['awayTeam'] == team]['homeTeamFt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['awayTeam'], self.data['awayTeam'].index)]
        # Halftime Away
        self.data['awayAverageHt'] = [round(
            self.data[
                self.data['awayTeam'] == team]['awayTeamHt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['awayTeam'], self.data['awayTeam'].index)]
        self.data['awayConcededHt'] = [round(
            self.data[
                self.data['awayTeam'] == team]['homeTeamHt'].expanding(2).mean()[index], 2)
            for team, index in zip(self.data['awayTeam'], self.data['awayTeam'].index)]
        return self

    def poisson_fulltime(self):
        self.data['FtUnder05'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0]), homeAvg) * poisson.pmf(
                            np.array(
                                [0]), awayAvg)))), 2)) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtUnder15'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 0, 1]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 1, 1]), awayAvg)))), 2)) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtUnder25'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 0, 1, 2, 0]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 1, 1, 0, 2]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtUnder35'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 1, 2, 0, 0, 0, 1]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 0, 0, 1, 1, 1, 2, 3, 2]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtUnder45'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 1, 2, 3, 4, 2, 3, 0, 0, 0, 0, 1, 1]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 1, 2, 0, 0, 0, 0, 1, 1, 1, 2, 3, 4, 2, 3]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtUnder55'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 1, 2, 3, 4, 5, 2, 3, 4, 3, 0, 0, 0, 0,
                                 0, 1, 1, 1, 2]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 1, 2, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 2, 3,
                                 4, 5, 2, 3, 4, 3]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtOver05'] = [100 - percent for percent in self.data['FtUnder05']]
        self.data['FtOver15'] = [100 - percent for percent in self.data['FtUnder15']]
        self.data['FtOver25'] = [100 - percent for percent in self.data['FtUnder25']]
        self.data['FtOver35'] = [100 - percent for percent in self.data['FtUnder35']]
        self.data['FtOver45'] = [100 - percent for percent in self.data['FtUnder45']]
        self.data['FtOver55'] = [100 - percent for percent in self.data['FtUnder55']]
        self.data['FtBTTSno'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4,
                                 5, 6, 7, 8, 9, 10]), awayAvg)))), 2)
                                  ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtBTTS'] = [100 - percent for percent in self.data['FtBTTSno']]
        self.data['FtHomeWin'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6,
                                 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9,
                                 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5,
                                 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 8,
                                 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtDraw'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), awayAvg)))), 2)
                                ) for homeAvg, awayAvg in
            zip(self.data['homeAverageFt'], self.data['awayAverageFt'])]
        self.data['FtAwayWin'] = [100 - (percentHome + percentAway) for percentHome, percentAway
                                  in zip(self.data['FtHomeWin'], self.data['FtDraw'])]

        return self

    def poisson_halftime(self):
        self.data['HtUnder05'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0]), homeAvg) * poisson.pmf(
                            np.array(
                                [0]), awayAvg)))), 2)
                               ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtUnder15'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 0, 1]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 1, 1]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtUnder25'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 0, 1, 2, 0]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 1, 1, 0, 2]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtUnder35'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 1, 2, 0, 0, 0, 1]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 0, 0, 1, 1, 1, 2, 3, 2]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtUnder45'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 1, 2, 3, 4, 2, 3, 0, 0, 0, 0, 1, 1]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 1, 2, 0, 0, 0, 0, 1, 1, 1, 2, 3, 4, 2, 3]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtUnder55'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 1, 2, 3, 4, 5, 2, 3, 4, 3, 0, 0, 0, 0,
                                 0, 1, 1, 1, 2]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 1, 2, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 2, 3,
                                 4, 5, 2, 3, 4, 3]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtOver05'] = [100 - percent for percent in self.data['HtUnder05']]
        self.data['HtOver15'] = [100 - percent for percent in self.data['HtUnder15']]
        self.data['HtOver25'] = [100 - percent for percent in self.data['HtUnder25']]
        self.data['HtOver35'] = [100 - percent for percent in self.data['HtUnder35']]
        self.data['HtOver45'] = [100 - percent for percent in self.data['HtUnder45']]
        self.data['HtOver55'] = [100 - percent for percent in self.data['HtUnder55']]
        self.data['HtBTTSno'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4,
                                 5, 6, 7, 8, 9, 10]), awayAvg)))), 2)
                                  ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtBTTS'] = [100 - percent for percent in self.data['HtBTTSno']]
        self.data['HtHomeWin'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6,
                                 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9,
                                 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5,
                                 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 8,
                                 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), awayAvg)))), 2)
                                   ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtDraw'] = [(round(
            float(
                np.array2string(
                    100 * sum(
                        poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), homeAvg) * poisson.pmf(
                            np.array(
                                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), awayAvg)))), 2)
                                ) for homeAvg, awayAvg in
            zip(self.data['homeAverageHt'], self.data['awayAverageHt'])]
        self.data['HtAwayWin'] = [100 - (percentHome + percentAway) for percentHome, percentAway
                                  in zip(self.data['HtHomeWin'], self.data['HtDraw'])]

        return self

    def export(self):
        self.data.to_csv('data/dataset.csv', index=False)


stats = Stats()

if __name__ == "__main__":
    stats.poisson_fulltime().poisson_halftime().export()
    print(f'Ran in {round(perf_counter() - start_stats, 2)} seconds')
