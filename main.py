from selenium.webdriver.chrome.options import Options
from datetime import date, timedelta, datetime
from scipy.stats import poisson
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
matches = pd.read_excel(os.path.join(__location__, 'database.xlsx'), sheet_name='Database')


class Football():

    def __init__(self, match_date=matches['Date'], team_home=matches['Home Team'], team_away=matches['Away Team'],
                 score_home=matches['Home Score'], score_away=matches['Away Score'], average_home=[],
                 average_away=[], poisson_05=[], poisson_15=[], poisson_25=[],
                 poisson_btts=[], poisson_bttsno=[]):
        self.match_date = match_date
        self.team_home = team_home
        self.team_away = team_away
        self.score_home = score_home
        self.score_away = score_away
        self.average_home = average_home
        self.average_away = average_away
        self.poisson_05 = poisson_05
        self.poisson_15 = poisson_15
        self.poisson_25 = poisson_25
        self.poisson_btts = poisson_btts
        self.poisson_bttsno = poisson_bttsno

    def scraper(self, match_date=[], team_home=[], team_away=[], score_home=[], score_away=[]):
        start_date = datetime.strptime(matches['Date'].tail(1).tolist()[0], '%Y-%m-%d')
        yesterday = str(date.today() - timedelta(days=1))
        print('Checking current database')
        if start_date != datetime.strptime(yesterday, '%Y-%m-%d'):
            end_date = datetime.strptime(str(date.today()), '%Y-%m-%d')

            print('Creating list of dates to scrape')

            def daterange(start_date, end_date):
                for n in range(int((end_date - start_date).days)):
                    yield (start_date + timedelta(n)).strftime('%Y-%m-%d')

            series_date = []
            series_home = []
            series_away = []
            series_hscore = []
            series_ascore = []

            print('Starting the scraping process')

            for single_date in daterange(start_date, end_date):
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

            print('Writing new data into the database file')

            new_matches = pd.DataFrame({'Date': series_date, 'Home Team': series_home, 'Home Score': series_hscore,
                                        'Away Team': series_away, 'Away Score': series_ascore})
            frames = [matches, new_matches]
            stats = pd.concat(frames, join='inner', ignore_index=True, sort=False)
            writer = pd.ExcelWriter(os.path.join(__location__, 'database.xlsx'), engine='xlsxwriter')
            stats.to_excel(writer, sheet_name='Database')
            writer.save()

            print('database.xlsx is ready')

        else:
            print('Database is already up to date')

    def under05(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)))
        return float(np.array2string(result))

    def under15(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
        return float(np.array2string(result))

    def under25(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(2, awayS)))
        return float(np.array2string(result))

    def btts(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
        return float(np.array2string(result))

    def bttsno(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
        return float(np.array2string(result))

    def averages(self, hteam=[], ateam=[], havg=[], aavg=[]):
        # use Team list index to filter scores and calc mean
        home = []
        away = []

        print('Calculating home averages')

        for h in hteam:
            home.append(h)
            temp_h = [np.NaN]
            h_index = matches.loc[matches['Home Team']==h].index.tolist()
            for i in range(1, len(h_index) + 1):
                df = matches['Home Score'].iloc[h_index[0:i]].mean()
                temp_h.append(df)
            havg.append(temp_h[home.count(h) - 1])

        print('Finished calculating home averages')

        print('Calculating away averages')

        for a in ateam:
            away.append(a)
            temp_a = [np.NaN]
            a_index = matches.loc[matches['Away Team']==a].index.tolist()
            for i in range(1, len(a_index) + 1):
                df = matches['Away Score'].iloc[a_index[0:i]].mean()
                temp_a.append(df)
            aavg.append(temp_a[away.count(a) - 1])

        print('Finished calculating away averages')

    def poissoncalc(self, havg = [], aavg = []):

        print('Calculating Poisson distribution')

        for x, y in zip(havg, aavg):
            football.poisson_05.append(football.under05(x, y))
            football.poisson_15.append(football.under15(x, y))
            football.poisson_25.append(football.under25(x, y))
            football.poisson_btts.append(football.btts(x, y))
            football.poisson_bttsno.append(football.bttsno(x, y))

        print('Done calculating Poisson distribution')

    def predictions(self, hteam=[], ateam=[], hscore = [], ascore = []):

        tomorrow = str(date.today() + timedelta(days=1))
        url = 'https://www.livescore.com/soccer/' + tomorrow

        print('Initializing Chrome')

        options = Options()
        options.headless = True
        driver = webdriver.Chrome(os.path.join(__location__, 'chromedriver.exe'), options=options)
        driver.get(url)
        driver.set_page_load_timeout(10)

        print("Extracting Tomorrow's matches")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        homeT = pd.Series([x.text for x in soup.find_all('div', class_='ply tright name') if x.text != '__home_team__'])
        awayT = pd.Series([x.text for x in soup.find_all('div', class_='ply name') if x.text != '__away_team__'])
        driver.close()

        print('Matches extracted')

        empty = pd.Series([np.NaN for x in homeT])
        hteam.append(homeT)
        ateam.append(awayT)
        hscore.append(empty)
        ascore.append(empty)
        haverage = []
        aaverage = []
        u05 = []
        u15 = []
        u25 = []
        btts = []
        bttsno = []

        print('Calculating averages')

        for h, a in zip(homeT, awayT):
            haverage.append(matches[matches['Home Team'] == h]['Home Score'].mean())
            aaverage.append(matches[matches['Away Team'] == a]['Away Score'].mean())

        print('Calculating Poisson distributions')

        for x, y in zip(haverage, aaverage):
            u05.append(football.under05(x, y))
            u15.append(football.under15(x, y))
            u25.append(football.under15(x, y))
            btts.append(football.btts(x, y))
            bttsno.append(football.bttsno(x, y))

        print('Writing output on predictions.xlsx')

        df = pd.DataFrame({'Home Team': homeT, 'Home Average': haverage, 'Away Team': awayT, 'Away Average': aaverage,
                           'Under 0.5': u05, 'Under 1.5': u15, 'Under 2.5': u25, 'BTTS': btts, 'BTTS No': bttsno})

        writer = pd.ExcelWriter(os.path.join(__location__, 'predictions.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print(df, 'predictions.xlsx is ready', sep='\n')

    def framebuilder(self, dates = [], homet = [], homescore = [],
                     homeavg = [], awayt = [], aways = [], awayavg = [],
                     poisson05 = [], poisson15 = [], poisson25 = [],
                     btts = [], bttsno = []):

        print('Building Dataframe')

        df = pd.DataFrame({
            'Date': dates, 'Home Team': homet, 'Away Team': awayt, 'Home Average': homeavg,  'Away Average': awayavg,
            'Under 0.5': poisson05, 'Under 1.5': poisson15, 'Under 2.5': poisson25, 'BTTS': btts, 'BTTS No': bttsno,
            'Home Score': homescore, 'Away Score': aways,})

        writer = pd.ExcelWriter(os.path.join(__location__, 'database.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print('database.xlsx is ready')

football = Football()

football.match_date = matches['Date'].tolist()
football.team_home = matches['Home Team'].tolist()
football.team_away = matches['Away Team'].tolist()
football.score_home = matches['Home Score'].tolist()
football.score_away = matches['Away Score'].tolist()

##### INDEX(NaN) NaN:LEN(LIST) REPLACE NAN WITH SCORE ON DB

football.scraper(football.match_date, football.team_home, football.team_away,
                 football.score_home, football.score_away)
football.averages(football.team_home, football.team_away, football.average_home, football.average_away)
football.poissoncalc(football.average_home, football.average_away)
football.framebuilder(football.match_date, football.team_home, football.score_home, football.average_home,
                      football.team_away, football.score_away, football.average_away,  football.poisson_05,
                      football.poisson_15, football.poisson_25, football.poisson_btts, football.poisson_bttsno)

football.predictions(football.team_home, football.team_away, football.score_away, football.score_home)
