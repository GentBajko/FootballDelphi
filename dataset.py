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
                 score_home=matches['Home Score'], score_away=matches['Away Score'], average_home=[], conceded_home=[],
                 average_away=[], conceded_away=[], poisson_u05=[], poisson_u15=[], poisson_u25=[], poisson_o05=[],
                 poisson_o15=[], poisson_o25=[], poisson_btts=[], poisson_bttsno=[]):
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
        self.poisson_btts = poisson_btts
        self.poisson_bttsno = poisson_bttsno
        self.poisson_o05 = poisson_o05
        self.poisson_o15 = poisson_o15
        self.poisson_o25 = poisson_o25

    def scraper(self):
        start_date = datetime.strptime(matches['Date'].tail(1).tolist()[0], '%Y-%m-%d')
        yesterday = str(date.today() - timedelta(days=1))

        currentDT = datetime.now()

        print('Checking current database', currentDT.strftime("%H:%M:%S"))

        if start_date != datetime.strptime(yesterday, '%Y-%m-%d'):
            end_date = datetime.strptime(str(date.today()), '%Y-%m-%d')

            currentDT = datetime.now()

            print('Creating list of dates to scrape', currentDT.strftime("%H:%M:%S"))

            def daterange(start_date, end_date):
                for n in range(int((end_date - start_date).days)):
                    yield (start_date + timedelta(n)).strftime('%Y-%m-%d')

            series_date = []
            series_home = []
            series_away = []
            series_hscore = []
            series_ascore = []

            currentDT = datetime.now()

            print('Starting the scraping process', currentDT.strftime("%H:%M:%S"))

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
                        series_hscore.append(float(hs.text))
                        series_ascore.append(float(aws.text))

                driver.close()

            print('New database entries:', pd.DataFrame({'Date': series_date, 'Home': series_home, 'Away': series_away,
                                                         'HS': series_hscore, 'AS': series_ascore}), sep='\n')

            currentDT = datetime.now()

            print('Writing new data into the database file', currentDT.strftime("%H:%M:%S"))

            new_matches = pd.DataFrame({'Date': series_date, 'Home Team': series_home, 'Home Score': series_hscore,
                                        'Away Team': series_away, 'Away Score': series_ascore})
            frames = [matches, new_matches]
            stats = pd.concat(frames, join='inner', ignore_index=True, sort=False)
            writer = pd.ExcelWriter(os.path.join(__location__, 'dataset.xlsx'), engine='xlsxwriter')
            stats.to_excel(writer, sheet_name='Database')
            writer.save()

            currentDT = datetime.now()

            print('dataset.xlsx is ready', currentDT.strftime("%H:%M:%S"))

        else:
            currentDT = datetime.now()

            print('Database is already up to date', currentDT.strftime("%H:%M:%S"))

    def under05(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)))
        return round(float(np.array2string(result)), 5)

    def over05(self, homeS, awayS):
        result = 100 - 100 * (((poisson.pmf(0, homeS) * poisson.pmf(0, awayS))))
        return round(float(np.array2string(result)), 5)

    def under15(self, homeS, awayS):
        result = 100 * (((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS))))
        return round(float(np.array2string(result)), 5)

    def over15(self, homeS, awayS):
        result = 100 - 100 * (((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS))))
        return round(float(np.array2string(result)), 5)

    def under25(self, homeS, awayS):
        result = 100 * (((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(2, awayS))))
        return round(float(np.array2string(result)), 5)

    def over25(self, homeS, awayS):
        result = 100 - 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(2, awayS)))
        return round(float(np.array2string(result)), 5)

    def btts(self, homeS, awayS):
        result = 100 - 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
        return round(float(np.array2string(result)), 5)

    def bttsno(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(1, awayS)))
        return round(float(np.array2string(result)), 5)

    def averages(self):
        # use Team list index to filter scores and calc mean
        home = []
        away = []

        currentDT = datetime.now()

        print('Calculating home averages', currentDT.strftime("%H:%M:%S"))

        for h in football.team_home:
            home.append(h)
            temp_h = [np.NaN]
            h_index = matches.loc[matches['Home Team'] == h].index.tolist()
            for i in range(1, len(h_index) + 1):
                df = matches['Home Score'].iloc[h_index[0:i]].mean()
                temp_h.append(df)
            football.average_home.append(round(temp_h[home.count(h) - 1] / 100, 5))

        home = []

        for h in football.team_home:
            home.append(h)
            temp_h = [np.NaN]
            h_index = matches.loc[matches['Home Team']==h].index.tolist()
            for i in range(1, len(h_index) + 1):
                df = matches['Away Score'].iloc[h_index[0:i]].mean()
                temp_h.append(df)
            football.conceded_home.append(round(temp_h[home.count(h) - 1] / 100, 5))

        currentDT = datetime.now()

        print('Finished calculating home averages', currentDT.strftime("%H:%M:%S"))

        currentDT = datetime.now()

        print('Calculating away averages', currentDT.strftime("%H:%M:%S"))

        for a in football.team_away:
            away.append(a)
            temp_a = [np.NaN]
            a_index = matches.loc[matches['Away Team']==a].index.tolist()
            for i in range(1, len(a_index) + 1):
                df = matches['Away Score'].iloc[a_index[0:i]].mean()
                temp_a.append(df)
            football.average_away.append(round(temp_a[away.count(a) - 1] / 100, 5))

        away = []

        for a in football.team_away:
            away.append(a)
            temp_a = [np.NaN]
            a_index = matches.loc[matches['Away Team'] == a].index.tolist()
            for i in range(1, len(a_index) + 1):
                df = matches['Home Score'].iloc[a_index[0:i]].mean()
                temp_a.append(df)
            football.average_away.append(round(temp_a[away.count(a) - 1] / 100, 5))

        currentDT = datetime.now()

        print('Finished calculating away averages', currentDT.strftime("%H:%M:%S"))

    def poissoncalc(self):

        currentDT = datetime.now()

        print('Calculating Poisson distribution', currentDT.strftime("%H:%M:%S"))

        for x, y in zip(football.average_home, football.average_away):
            football.poisson_o05.append(football.over05(x, y))
            football.poisson_u05.append(football.under05(x, y))
            football.poisson_o15.append(football.over15(x, y))
            football.poisson_u15.append(football.under15(x, y))
            football.poisson_o25.append(football.over25(x, y))
            football.poisson_u25.append(football.under25(x, y))
            football.poisson_btts.append(football.btts(x, y))
            football.poisson_bttsno.append(football.bttsno(x, y))

        currentDT = datetime.now()

        print('Done calculating Poisson distribution', currentDT.strftime("%H:%M:%S"))

    def predictions(self, hteam=[], ateam=[], hscore = [], ascore = []):

        tomorrow = str(date.today() + timedelta(days=1))
        url = 'https://www.livescore.com/soccer/' + tomorrow

        currentDT = datetime.now()

        print('Initializing Chrome', currentDT.strftime("%H:%M:%S"))

        options = Options()
        options.headless = True
        driver = webdriver.Chrome(os.path.join(__location__, 'chromedriver.exe'), options=options)
        driver.get(url)
        driver.set_page_load_timeout(10)

        currentDT = datetime.now()

        print("Extracting Tomorrow's matches", currentDT.strftime("%H:%M:%S"))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        homeT = pd.Series([x.text for x in soup.find_all('div', class_='ply tright name') if x.text != '__home_team__'])
        awayT = pd.Series([x.text for x in soup.find_all('div', class_='ply name') if x.text != '__away_team__'])
        driver.close()

        currentDT = datetime.now()

        print('Matches extracted', currentDT.strftime("%H:%M:%S"))

        empty = pd.Series([np.NaN for x in homeT])
        hteam.append(homeT)
        ateam.append(awayT)
        hscore.append(empty)
        ascore.append(empty)
        haverage = []
        aaverage = []
        u05 = []
        o05 = []
        u15 = []
        o15 = []
        u25 = []
        o25 = []
        btts = []
        bttsno = []

        currentDT = datetime.now()

        print('Calculating averages', currentDT.strftime("%H:%M:%S"))

        for h, a in zip(homeT, awayT):
            haverage.append(matches[matches['Home Team'] == h]['Home Score'].mean())
            aaverage.append(matches[matches['Away Team'] == a]['Away Score'].mean())

        currentDT = datetime.now()

        print('Calculating Poisson distributions', currentDT.strftime("%H:%M:%S"))

        for x, y in zip(haverage, aaverage):
            u05.append(football.under05(x, y))
            o05.append(football.over05(x, y))
            u15.append(football.under15(x, y))
            o15.append(football.over15(x, y))
            u25.append(football.under25(x, y))
            o25.append(football.over25(x, y))
            btts.append(football.btts(x, y))
            bttsno.append(football.bttsno(x, y))

        currentDT = datetime.now()

        print('Writing output on predictions.xlsx', currentDT.strftime("%H:%M:%S"))

        df = pd.DataFrame({'Home Team': homeT, 'Home Average': haverage, 'Away Team': awayT, 'Away Average': aaverage,
                           'Over 0.5': o05, 'Under 0.5': u05, 'Over 1.5': o15, 'Under 1.5': u15, 'Over 2.5': o25,
                           'Under 2.5': u25, 'BTTS': btts, 'BTTS No': bttsno})

        writer = pd.ExcelWriter(os.path.join(__location__, 'predictions.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print(df, 'predictions.xlsx is ready', currentDT.strftime("%H:%M:%S"), sep='\n')

    def framebuilder(self, filename):

        currentDT = datetime.now()

        print('Building Dataframe', currentDT.strftime("%H:%M:%S"))

        df = pd.DataFrame({
            'Date': football.match_date, 'Home Team': football.team_home, 'Away Team': football.team_away,
            'Home Average': football.average_home,  'Away Average': football.average_away,
            'Over 0.5': football.poisson_o05, 'Under 0.5': football.poisson_u05, 'Over 1.5': football.poisson_o15,
            'Under 1.5': football.poisson_u15, 'Over 2.5': football.poisson_o25, 'Under 2.5': football.poisson_u25,
            'BTTS': football.poisson_btts, 'BTTS No': football.poisson_bttsno, 'Home Score': football.score_home,
            'Away Score': football.score_away})

        writer = pd.ExcelWriter(os.path.join(__location__, 'dataset.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        currentDT = datetime.now()

        print(' '.join(filename, '.xlsx is ready'),currentDT.strftime("%H:%M:%S"))


        df = df.dropna()
        writer = pd.ExcelWriter(os.path.join(__location__, 'dropna.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        currentDT = datetime.now()

        print('dropna.xlsx is ready', currentDT.strftime("%H:%M:%S"))


football = Football()

football.match_date = matches['Date']
football.team_home = matches['Home Team']
football.team_away = matches['Away Team']
football.score_home = matches['Home Score']
football.score_away = matches['Away Score']

##### INDEX(NaN) NaN:LEN(LIST) REPLACE NAN WITH SCORE ON DB

football.scraper()
football.averages()
football.poissoncalc()
football.framebuilder('dataset')
