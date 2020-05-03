from selenium.webdriver.chrome.options import Options
from datetime import date, timedelta, datetime
from scipy.stats import poisson
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os, sklearn.preprocessing

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
matches = pd.read_excel(os.path.join(__location__, 'database.xlsx'), sheet_name='Database')


class Football():

    def __init__(self, match_date=matches['Date'], team_home=matches['Home Team'], team_away=matches['Away Team'],
                 score_home=matches['Home Score'], score_away=matches['Away Score'], average_home=[], conceded_home=[],
                 average_away=[], conceded_away=[], poisson_u05=[], poisson_u15=[], poisson_u25=[], poisson_o05=[],
                 poisson_o15=[], poisson_o25=[], poisson_btts=[], poisson_bttsno=[], poisson_homewin=[],
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
        self.poisson_btts = poisson_btts
        self.poisson_bttsno = poisson_bttsno
        self.poisson_o05 = poisson_o05
        self.poisson_o15 = poisson_o15
        self.poisson_o25 = poisson_o25
        self.poisson_homewin = poisson_homewin
        self.poisson_awaywin = poisson_awaywin
        self.poisson_draw = poisson_draw

    def scraper(self):
        start_date = datetime.strptime(matches['Date'].tail(1).tolist()[0], '%Y-%m-%d')
        yesterday = str(date.today() - timedelta(days=1))

        print('Checking current database', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        if start_date != datetime.strptime(yesterday, '%Y-%m-%d'):
            end_date = datetime.strptime(str(date.today()), '%Y-%m-%d')


            print('Creating list of dates to scrape', datetime.now().strftime("%H:%M:%S"), sep=' - ')

            def daterange(start_date, end_date):
                for n in range(int((end_date - start_date).days)):
                    yield (start_date + timedelta(n)).strftime('%Y-%m-%d')

            series_date = []
            series_home = []
            series_away = []
            series_hscore = []
            series_ascore = []


            print('Starting the scraping process', datetime.now().strftime("%H:%M:%S"), sep=' - ')

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
                        series_hscore.append(hs.text)
                        series_ascore.append(aws.text)

                driver.close()

            print('New database entries:', pd.DataFrame({'Date': series_date, 'Home': series_home, 'Away': series_away,
                                                         'HS': series_hscore, 'AS': series_ascore}), sep='\n')


            print('Writing new data into the database file', datetime.now().strftime("%H:%M:%S"), sep=' - ')

            new_matches = pd.DataFrame({'Date': series_date, 'Home Team': series_home, 'Home Score': series_hscore,
                                        'Away Team': series_away, 'Away Score': series_ascore})
            frames = [matches, new_matches]
            stats = pd.concat(frames, join='inner', ignore_index=True, sort=False)
            writer = pd.ExcelWriter(os.path.join(__location__, 'dataset.xlsx'), engine='xlsxwriter')
            stats.to_excel(writer, sheet_name='Database')
            writer.save()


            print('dataset.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        else:

            print('Database is already up to date', datetime.now().strftime("%H:%M:%S"), sep=' - ')

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

    def homewin(self, homeS, awayS):
        result = 100 * ((poisson.pmf(1, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(3, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(4, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(5, homeS) * poisson.pmf(0, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(3, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(4, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(5, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(3, homeS) * poisson.pmf(2, awayS)) +
                        (poisson.pmf(4, homeS) * poisson.pmf(2, awayS)) +
                        (poisson.pmf(5, homeS) * poisson.pmf(2, awayS)) +
                        (poisson.pmf(4, homeS) * poisson.pmf(3, awayS)) +
                        (poisson.pmf(5, homeS) * poisson.pmf(3, awayS)) +
                        (poisson.pmf(5, homeS) * poisson.pmf(4, awayS)))
        return round(float(np.array2string(result)), 5)

    def awaywin(self, homeS, awayS):
        result = 100 * ((poisson.pmf(0, homeS) * poisson.pmf(1, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(2, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(3, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(4, awayS)) +
                        (poisson.pmf(0, homeS) * poisson.pmf(5, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(2, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(3, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(4, awayS)) +
                        (poisson.pmf(1, homeS) * poisson.pmf(5, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(3, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(4, awayS)) +
                        (poisson.pmf(2, homeS) * poisson.pmf(5, awayS)) +
                        (poisson.pmf(3, homeS) * poisson.pmf(4, awayS)) +
                        (poisson.pmf(3, homeS) * poisson.pmf(5, awayS)) +
                        (poisson.pmf(4, homeS) * poisson.pmf(5, awayS)))
        return round(float(np.array2string(result)), 5)

    def averages(self):
        # use Team list index to filter scores and calc mean
        home = []
        away = []

        print('Calculating home averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for h in football.team_home:
            home.append(h)
            temp_h = [np.NaN]
            h_index = matches.loc[matches['Home Team'] == h].index.tolist()
            for i in range(1, len(h_index) + 1):
                df = matches['Home Score'].iloc[h_index[0:i]].mean()
                temp_h.append(df)
            football.average_home.append(round(temp_h[home.count(h) - 1], 5))

        home = []

        for h in football.team_home:
            home.append(h)
            temp_h = [np.NaN]
            h_index = matches.loc[matches['Home Team'] == h].index.tolist()
            for i in range(1, len(h_index) + 1):
                df = matches['Away Score'].iloc[h_index[0:i]].mean()
                temp_h.append(df)
            football.conceded_home.append(round(temp_h[home.count(h) - 1], 5))

        print('Finished calculating home averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        print('Calculating away averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for a in football.team_away:
            away.append(a)
            temp_a = [np.NaN]
            a_index = matches.loc[matches['Away Team'] == a].index.tolist()
            for i in range(1, len(a_index) + 1):
                df = matches['Away Score'].iloc[a_index[0:i]].mean()
                temp_a.append(df)
            football.average_away.append(round(temp_a[away.count(a) - 1], 5))

        away = []

        for a in football.team_away:
            away.append(a)
            temp_a = [np.NaN]
            a_index = matches.loc[matches['Away Team'] == a].index.tolist()
            for i in range(1, len(a_index) + 1):
                df = matches['Home Score'].iloc[a_index[0:i]].mean()
                temp_a.append(df)
            football.conceded_away.append(round(temp_a[away.count(a) - 1], 5))

        print('Finished calculating away averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

    def poisson(self):

        print('Calculating Poisson distribution', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for x, y in zip(football.average_home, football.average_away):
            football.poisson_o05.append(football.over05(x, y))
            football.poisson_u05.append(football.under05(x, y))
            football.poisson_o15.append(football.over15(x, y))
            football.poisson_u15.append(football.under15(x, y))
            football.poisson_o25.append(football.over25(x, y))
            football.poisson_u25.append(football.under25(x, y))
            football.poisson_btts.append(football.btts(x, y))
            football.poisson_bttsno.append(football.bttsno(x, y))
            # football.poisson_homewin.append(football.homewin(x, y))
            # football.poisson_awaywin.append(football.awaywin(x, y))
            # football.poisson_draw.append(100 - (football.homewin(x, y) + football.awaywin(x, y)))

        print('Done calculating Poisson distribution', datetime.now().strftime("%H:%M:%S"), sep=' - ')

    def predictions(self, hteam=[], ateam=[], hscore=[], ascore=[]):

        tomorrow = str(date.today() + timedelta(days=1))
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

        empty = pd.Series([np.NaN for x in homeT])
        hteam.append(homeT)
        ateam.append(awayT)
        hscore.append(empty)
        ascore.append(empty)
        haverage = []
        aaverage = []
        hconceded = []
        aconceded = []
        u05 = []
        o05 = []
        u15 = []
        o15 = []
        u25 = []
        o25 = []
        btts = []
        bttsno = []

        print('Calculating averages', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for h, a in zip(homeT, awayT):
            haverage.append(matches[matches['Home Team'] == h]['Home Score'].mean())
            aaverage.append(matches[matches['Away Team'] == a]['Away Score'].mean())
            hconceded.append(matches[matches['Home Team'] == h]['Away Score'].mean())
            aconceded.append(matches[matches['Away Team'] == a]['Home Score'].mean())

        print('Calculating Poisson distributions', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        for x, y in zip(haverage, aaverage):
            u05.append(football.under05(x, y))
            o05.append(football.over05(x, y))
            u15.append(football.under15(x, y))
            o15.append(football.over15(x, y))
            u25.append(football.under25(x, y))
            o25.append(football.over25(x, y))
            btts.append(football.btts(x, y))
            bttsno.append(football.bttsno(x, y))

        print('Writing output on predictions.xlsx', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        df = pd.DataFrame({
            'Home Team': homeT,  'Away Team': awayT, 'Home Average': haverage, 'Away Average': aaverage,
            'Home Conceded': hconceded, 'Away Conceded': aconceded, 'Over 0.5': o05, 'Under 0.5': u05, 'Over 1.5': o15,
            'Under 1.5': u15, 'Over 2.5': o25, 'Under 2.5': u25, 'BTTS': btts, 'BTTS No': bttsno
        })

        writer = pd.ExcelWriter(os.path.join(__location__, 'predictions.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print(df, 'predictions.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep='\n')

    def database(self):

        print('Building Database', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        df = pd.DataFrame({
            'Date': football.match_date, 'Home Team': football.team_home, 'Away Team': football.team_away,
            'Home Average': football.average_home, 'Away Average': football.average_away,
            'AVG Conceded Home': football.conceded_home, 'AVG Conceded Away': football.conceded_away,
            'Over 0.5': football.poisson_o05, 'Under 0.5': football.poisson_u05, 'Over 1.5': football.poisson_o15,
            'Under 1.5': football.poisson_u15, 'Over 2.5': football.poisson_o25, 'Under 2.5': football.poisson_u25,
            'BTTS': football.poisson_btts, 'BTTS No': football.poisson_bttsno,
            'Home Score': football.score_home, 'Away Score': football.score_away})

        writer = pd.ExcelWriter(os.path.join(__location__, 'database.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Database')
        writer.save()

        print('database.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep=' - ')

    def dataset(self):

        df = matches.dropna()
        print(df)

        print('Encoding teams', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        teams = set()
        for home, away in zip(df['Home Team'], df['Away Team']):
            teams.add(home)
            teams.add(away)
        encoded_teams = {k: v for (k, v) in zip(teams, range(len(teams) + 1))}
        home_team = [encoded_teams[x] for x in df['Home Team']]
        away_team = [encoded_teams[x] for x in df['Away Team']]
        winner = []

        for x, y in zip(df['Home Score'], df['Away Score']):
            if x > y:
                winner.append(1)
            else:
                winner.append(0)

        date = pd.to_datetime(df['Date'])
        date = pd.Series(date).dt.dayofyear
        date = pd.Series(sklearn.preprocessing.normalize([date.to_numpy()], norm='max',
                                                         axis=1).flatten(order='C'))
        home_avg = pd.Series(sklearn.preprocessing.normalize([df['Home Average']], norm='max',
                                                             axis=1).flatten(order='C'))
        away_avg = pd.Series(sklearn.preprocessing.normalize([df['Away Average']], norm='max',
                                                             axis=1).flatten(order='C'))
        home_conceded = pd.Series(sklearn.preprocessing.normalize([df['AVG Conceded Home']], norm='max',
                                                                   axis=1).flatten(order='C'))
        away_conceded = pd.Series(sklearn.preprocessing.normalize([df['AVG Conceded Away']], norm='max',
                                                                   axis=1).flatten(order='C'))
        o05 = pd.Series(sklearn.preprocessing.normalize([df['Over 0.5']], norm='max',
                                                        axis=1).flatten(order='C'))
        u05 = pd.Series(sklearn.preprocessing.normalize([df['Under 0.5']], norm='max',
                                                        axis=1).flatten(order='C'))
        o15 = pd.Series(sklearn.preprocessing.normalize([df['Over 1.5']], norm='max',
                                                        axis=1).flatten(order='C'))
        u15 = pd.Series(sklearn.preprocessing.normalize([df['Under 1.5']], norm='max',
                                                        axis=1).flatten(order='C'))
        o25 = pd.Series(sklearn.preprocessing.normalize([df['Over 2.5']], norm='max',
                                                        axis=1).flatten(order='C'))
        u25 = pd.Series(sklearn.preprocessing.normalize([df['Under 2.5']], norm='max',
                                                        axis=1).flatten(order='C'))
        btts = pd.Series(sklearn.preprocessing.normalize([df['BTTS']], norm='max',
                                                         axis=1).flatten(order='C'))
        bttsno = pd.Series(sklearn.preprocessing.normalize([df['BTTS No']], norm='max',
                                                           axis=1).flatten(order='C'))
        home_score = pd.Series(sklearn.preprocessing.normalize([df['Home Score']], norm='max',
                                                               axis=1).flatten(order='C'))
        away_score = pd.Series(sklearn.preprocessing.normalize([df['Away Score']], norm='max',
                                                               axis=1).flatten(order='C'))
        home = pd.Series(sklearn.preprocessing.normalize([home_team], norm='max',
                                                         axis=1).flatten(order='C'))
        away = pd.Series(sklearn.preprocessing.normalize([away_team], norm='max',
                                                         axis=1).flatten(order='C'))
        df = pd.DataFrame({
            'Date': date, 'Home Team': home, 'Away Team': away,'Home Average': home_avg,
            'Away Average': away_avg, 'AVG Conceded Home': home_conceded, 'AVG Conceded Away': away_conceded,
            'Over 0.5': o05, 'Under 0.5': u05, 'Over 1.5': o15, 'Under 1.5': u15, 'Over 2.5': o25, 'Under 2.5': u25,
            'BTTS': btts, 'BTTS No': bttsno, 'Home Score': home_score, 'Away Score': away_score, 'Result': winner
        })

        writer = pd.ExcelWriter(os.path.join(__location__, 'dataset.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Dataset')
        writer.save()

        print('dataset.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep=' - ')

        df = matches.dropna()

        date = pd.to_datetime(df['Date'])
        date = pd.Series(date).dt.dayofyear
        home_avg = df['Home Average'].tolist()
        away_avg = df['Away Average'].tolist()
        home_conceded = df['AVG Conceded Home'].tolist()
        away_conceded = df['AVG Conceded Away'].tolist()
        o05 = df['Over 0.5'].tolist()
        u05 = df['Under 0.5'].tolist()
        o15 = df['Over 1.5'].tolist()
        u15 = df['Under 1.5'].tolist()
        o25 = df['Over 2.5'].tolist()
        u25 = df['Under 2.5'].tolist()
        btts = df['BTTS'].tolist()
        bttsno = df['BTTS No'].tolist()
        home_score = df['Home Score'].tolist()
        away_score = df['Away Score'].tolist()

        df = pd.DataFrame({
            'Date': date, 'Home Team': home_team, 'Away Team': away_team, 'Home Average': home_avg,
            'Away Average': away_avg, 'AVG Conceded Home': home_conceded, 'AVG Conceded Away': away_conceded,
            'Over 0.5': o05, 'Under 0.5': u05, 'Over 1.5': o15, 'Under 1.5': u15, 'Over 2.5': o25, 'Under 2.5': u25,
            'BTTS': btts, 'BTTS No': bttsno, 'Home Score': home_score, 'Away Score': away_score, 'Result': winner
        })

        writer = pd.ExcelWriter(os.path.join(__location__, 'data.xlsx'),
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Dataset')
        writer.save()

        print('data.xlsx is ready', datetime.now().strftime("%H:%M:%S"), sep=' - ')

football = Football()

football.match_date = matches['Date']
football.team_home = matches['Home Team']
football.team_away = matches['Away Team']
football.score_home = matches['Home Score']
football.score_away = matches['Away Score']

##### INDEX(NaN) NaN:LEN(LIST) REPLACE NAN WITH SCORE ON DB

football.scraper()
football.averages()
football.poisson()
football.database()
football.dataset()
football.predictions()
