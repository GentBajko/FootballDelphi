import time

start = time.perf_counter()

import os
from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from scipy.stats import poisson
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
matches = pd.read_excel(os.path.join(__location__, 'database.xlsx'), sheet_name='Database')
np.warnings.filterwarnings('ignore')

class Football():

    def __init__(self, match_date=matches['Date'], team_home=matches['Home Team'], team_away=matches['Away Team'],
                 score_home=matches['Home Score'], score_away=matches['Away Score'], average_home=[], conceded_home=[],
                 average_away=[], conceded_away=[], poisson_u05=[], poisson_u15=[], poisson_u25=[],  poisson_u35=[],
                 poisson_u45=[],  poisson_u55=[], poisson_o05=[], poisson_o15=[], poisson_o25=[], poisson_o35=[],
                 poisson_o45=[], poisson_o55=[], poisson_btts=[], poisson_bttsno=[], poisson_homewin=[],
                 poisson_awaywin=[], poisson_draw=[]):
        self.match_date = match_date
        self.team_home = team_home
        self.team_away = team_away
        self.score_home = score_home
        self.score_away = score_away
        self.average_home = average_home
        self.conceded_home = conceded_home
        self.conceded_away = conceded_away
        self.average_away = average_away
        self.poisson_u05 = poisson_u05
        self.poisson_u15 = poisson_u15
        self.poisson_u25 = poisson_u25
        self.poisson_u35 = poisson_u35
        self.poisson_u45 = poisson_u45
        self.poisson_u55 = poisson_u55
        self.poisson_btts = poisson_btts
        self.poisson_bttsno = poisson_bttsno
        self.poisson_o05 = poisson_o05
        self.poisson_o15 = poisson_o15
        self.poisson_o25 = poisson_o25
        self.poisson_o35 = poisson_o35
        self.poisson_o45 = poisson_o45
        self.poisson_o55 = poisson_o55
        self.poisson_homewin = poisson_homewin
        self.poisson_awaywin = poisson_awaywin
        self.poisson_draw = poisson_draw


    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield (start_date + timedelta(n)).strftime('%Y-%m-%d')

    def scraper(self):
        start_date = datetime.strptime(matches['Date'].tail(1).tolist()[0], '%Y-%m-%d')
        yesterday = str(date.today() - timedelta(days=1))

        print('Checking current database', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        if start_date != datetime.strptime(yesterday, '%Y-%m-%d'):
            end_date = datetime.strptime(str(date.today()), '%Y-%m-%d')

            print('Creating list of dates to scrape', datetime.now().strftime("%H:%M:%S"), sep=' - ')

            print('Starting the scraping process', datetime.now().strftime("%H:%M:%S"), sep=' - ')

            series_date = []
            series_home = []
            series_away = []
            series_hscore = []
            series_ascore = []

            for single_date in football.daterange(start_date, end_date):
                day = str(datetime.strptime(str(single_date)[0:10], '%Y-%m-%d'))
                url = 'https://www.livescore.com/soccer/' + str(day)[0:10]

                options = Options()
                options.headless = True
                driver = webdriver.Chrome(os.path.join(__location__, 'chromedriver.exe'), options=options)
                driver.get(url)
                driver.set_page_load_timeout(10)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                homeT = soup.find_all('div', class_='ply tright name')
                awayT = soup.find_all('div', class_='ply name')
                hScore = soup.find_all('span', class_='hom')
                aScore = soup.find_all('span', class_='awy')

                for h, a, hs, aws in zip(homeT, awayT, hScore, aScore):
                    if h.text == '__home_team__' or hs.text == '?':
                        pass
                    else:
                        series_date.append(str(day)[0:10])
                        series_home.append(h.text.replace(' *', ''))
                        series_away.append(a.text.replace(' *', ''))
                        series_hscore.append(int(hs.text))
                        series_ascore.append(int(aws.text))

                driver.close()

            print('New database entries:', pd.DataFrame({'Date': series_date, 'Home': series_home, 'Away': series_away,
                                                         'HS': series_hscore, 'AS': series_ascore}), sep='\n')

            print('Writing new data into the database file', datetime.now().strftime("%H:%M:%S"), sep=' - ')

            new_matches = pd.DataFrame({'Date': series_date, 'Home Team': series_home, 'Home Score': series_hscore,
                                        'Away Team': series_away, 'Away Score': series_ascore})
            frames = [matches, new_matches]
            stats = pd.concat(frames, join='inner', ignore_index=True, sort=False)
            writer = pd.ExcelWriter(os.path.join(__location__, 'database.xlsx'), engine='xlsxwriter')
            stats.to_excel(writer, sheet_name='Database')
            writer.save()

            print('database.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        else:

            print('Database is already up to date', datetime.now().strftime("%H:%M:%S"), sep=' - ')


    def poissondist(self, home_avg, away_avg):

        under05 = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0]), home_avg) *
            poisson.pmf(np.array([0]), away_avg)))), 5
                        )
        under15 = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 0, 1]), home_avg) *
            poisson.pmf(np.array([0, 0, 1, 1]), away_avg)))), 5
                        )
        under25 = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 0, 1, 2, 0]), home_avg) *
            poisson.pmf(np.array([0, 0, 1, 1, 0, 2]), away_avg)))), 5
                        )
        under35 = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 2, 3, 1, 2, 0, 0, 0, 1]), home_avg) *
            poisson.pmf(np.array([0, 0, 0, 0, 1, 1, 1, 2, 3, 2]), away_avg)))), 5
                        )
        under45 = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 2, 1, 2, 3, 4, 2, 3, 0, 0, 0, 0, 1, 1]), home_avg) *
            poisson.pmf(np.array([0, 1, 2, 0, 0, 0, 0, 1, 1, 1, 2, 3, 4, 2, 3]), away_avg)))), 5
                        )
        under55 = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 2, 1, 2, 3, 4, 5, 2, 3, 4, 3, 0, 0, 0, 0, 0, 1, 1, 1, 2]), home_avg) *
            poisson.pmf(np.array([0, 1, 2, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 2, 3, 4, 5, 2, 3, 4, 3]), away_avg)))), 5
                        )
        over05 = 100 - under05

        over15 = 100 - under15

        over25 = 100 - under25

        over35 = 100 - under35

        over45 = 100 - under45

        over55 = 100 - under55

        bttsno = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), home_avg) *
            poisson.pmf(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), away_avg)))), 5
                        )

        btts = 100 - bttsno

        homewin = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6,
                                  7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9,
                                  10, 10, 10, 10, 10, 10, 10, 10, 10, 10]), home_avg) *
            poisson.pmf(np.array([0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5,
                                  0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 8,
                                  0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), away_avg)))), 5
                        )

        draw = round(float(np.array2string(100 * sum(
            poisson.pmf(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), home_avg) *
            poisson.pmf(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), away_avg)))), 5
                        )

        awaywin = 100 - (homewin + draw)

        return {'Under 0.5': under05, 'Over 0.5': over05, 'Under 1.5': under15, 'Over 1.5': over15,
                'Under 2.5': under25,
                'Over 2.5': over25, 'Under 3.5': under35, 'Over 3.5': over35, 'Under 4.5': under45, 'Over 4.5': over45,
                'Under 5.5': under55, 'Over 5.5': over55, 'BTTS': bttsno, 'BTTSno': btts,
                'Home Win': homewin, 'Away Win': awaywin, 'Draw': draw}


    def averages(self):

        print('Calculating home averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        matches = pd.read_excel(os.path.join(__location__, 'database.xlsx'), sheet_name='Database')

        home_avg = []
        home_conceded = []

        for team in matches['Home Team'].unique():
            home_avg.append(matches[matches['Home Team'] == team]['Home Score'].expanding(2).mean())
            home_conceded.append(matches[matches['Home Team'] == team]['Away Score'].expanding(2).mean())

        football.average_home = pd.concat(home_avg).sort_index()
        football.conceded_home = pd.concat(home_conceded).sort_index()

        print('Finished calculating home averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        print('Calculating away averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        away_avg = []
        away_conceded = []

        for team in matches['Away Team'].unique():
            away_avg.append(matches[matches['Away Team'] == team]['Away Score'].expanding(2).mean())
            away_conceded.append(matches[matches['Away Team'] == team]['Home Score'].expanding(2).mean())

        football.average_away = pd.concat(away_avg).sort_index()
        football.conceded_away = pd.concat(away_conceded).sort_index()

        print(football.score_home, football.score_away)
        print('Finished calculating away averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')


    def poissoncalc(self):

        print('Calculating Poisson distribution', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for home_avg, away_avg in zip(football.average_home, football.average_away):
            temp_poisson = football.poissondist(home_avg, away_avg)
            football.poisson_o05.append(temp_poisson['Over 0.5'])
            football.poisson_u05.append(temp_poisson['Under 0.5'])
            football.poisson_o15.append(temp_poisson['Over 1.5'])
            football.poisson_u15.append(temp_poisson['Under 1.5'])
            football.poisson_o25.append(temp_poisson['Over 2.5'])
            football.poisson_u25.append(temp_poisson['Under 2.5'])
            football.poisson_o35.append(temp_poisson['Over 3.5'])
            football.poisson_u35.append(temp_poisson['Under 3.5'])
            football.poisson_o45.append(temp_poisson['Over 4.5'])
            football.poisson_u45.append(temp_poisson['Under 4.5'])
            football.poisson_o55.append(temp_poisson['Over 5.5'])
            football.poisson_u55.append(temp_poisson['Under 5.5'])
            football.poisson_btts.append(temp_poisson['BTTS'])
            football.poisson_bttsno.append(temp_poisson['BTTSno'])
            football.poisson_homewin.append(temp_poisson['Home Win'])
            football.poisson_awaywin.append(temp_poisson['Away Win'])
            football.poisson_draw.append(temp_poisson['Draw'])

        print('Done calculating Poisson distribution', datetime.now().strftime("%H:%M:%S"), sep=' - ')


    def builder(self):


        print('Building Database', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        df = pd.DataFrame({
            'Date': football.match_date, 'Home Team': football.team_home, 'Away Team': football.team_away,
            'Home Average': football.average_home, 'Away Average': football.average_away,
            'AVG Conceded Home': football.conceded_home, 'AVG Conceded Away': football.conceded_away,
            'Home Win': football.poisson_homewin, 'Draw': football.poisson_draw, 'Away Win': football.poisson_awaywin,
            'Over 0.5': football.poisson_o05, 'Under 0.5': football.poisson_u05, 'Over 1.5': football.poisson_o15,
            'Under 1.5': football.poisson_u15, 'Over 2.5': football.poisson_o25, 'Under 2.5': football.poisson_u25,
            'Over 3.5': football.poisson_o35, 'Under 3.5': football.poisson_u35, 'Over 4.5': football.poisson_o45,
            'Under 4.5': football.poisson_u45, 'Over 5.5': football.poisson_o55, 'Under 5.5': football.poisson_u55,
            'BTTS': football.poisson_btts, 'BTTS No': football.poisson_bttsno,
            'Home Score': football.score_home, 'Away Score': football.score_away})

        print(df)

        writer = pd.ExcelWriter(os.path.join(__location__, 'database.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print('database.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep=' - ')


    def upcoming(self):

        tomorrow = str(date.today() + timedelta(days=1))
        week_length = str(date.today() + timedelta(days=7))
        url = 'https://www.livescore.com/soccer/' + tomorrow

        print('Initializing Chrome', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        options = Options()
        options.headless = True
        driver = webdriver.Chrome(os.path.join(__location__, 'chromedriver.exe'), options=options)
        driver.get(url)
        driver.set_page_load_timeout(10)


        print("Extracting Tomorrow's matches", datetime.now().strftime("%H:%M:%S"), sep=' - ')

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        homeT = pd.Series([x.text for x in soup.find_all('div', class_='ply tright name') if x.text != '__home_team__'])
        awayT = pd.Series([x.text for x in soup.find_all('div', class_='ply name') if x.text != '__away_team__'])
        driver.close()

        print('Matches extracted', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        empty = pd.Series([np.NaN for _ in homeT])
        u05 = []
        o05 = []
        u15 = []
        o15 = []
        u25 = []
        o25 = []
        btts = []
        bttsno = []

        print('Calculating averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        haverage = [matches[matches['Home Team'] == x]['Home Score'].mean() for x in homeT]
        aaverage = [matches[matches['Away Team'] == x]['Away Score'].mean() for x in awayT]
        hconceded = [matches[matches['Home Team'] == x]['Away Score'].mean() for x in homeT]
        aconceded = [matches[matches['Away Team'] == x]['Home Score'].mean() for x in awayT]
        print(len(haverage), len(aaverage), sep='\n')

        print('Calculating Poisson distributions', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for x, y in zip(haverage, aaverage):
            temp_poisson = football.poissondist(x, y)
            u05.append(temp_poisson['Under 0.5'])
            o05.append(temp_poisson['Over 0.5'])
            u15.append(temp_poisson['Under 1.5'])
            o15.append(temp_poisson['Over 1.5'])
            u25.append(temp_poisson['Under 1.5'])
            o25.append(temp_poisson['Over 1.5'])
            btts.append(temp_poisson['BTTS'])
            bttsno.append(temp_poisson['BTTSno'])


        print('Writing output on upcoming.xlsx', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        df = pd.DataFrame({
            'Home Team': homeT, 'Away Team': awayT, 'Home Average': haverage, 'Away Average': aaverage,
            'Home Conceded': hconceded, 'Away Conceded': aconceded, 'Over 0.5': o05, 'Under 0.5': u05, 'Over 1.5': o15,
            'Under 1.5': u15, 'Over 2.5': o25, 'Under 2.5': u25, 'BTTS': btts, 'BTTS No': bttsno
        })

        writer = pd.ExcelWriter(os.path.join(__location__, 'upcoming.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print(df, 'upcoming.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep='\n')


football = Football()
football.match_date = matches['Date']
football.team_home = matches['Home Team']
football.team_away = matches['Away Team']
football.score_home = matches['Home Score']
football.score_away = matches['Away Score']

football.scraper()
football.averages()
football.poissoncalc()
football.builder()
# football.dataset()
football.upcoming()
finish = time.perf_counter()

print(f"Finished in {(finish - start) // 60} minute(s) and {round((finish - start) % 60, 2)} second(s)")
