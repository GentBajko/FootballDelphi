from selenium import webdriver
from datetime import datetime, timedelta
import pandas as pd
import os


class Scraper:
    def __init__(self, method, start_date=None,
                 end_date=None):
        self.method = method
        if self.method.lower() == 'upcoming':
            self.start_date = (datetime.today() + timedelta(days=1))
            self.end_date = (datetime.today() + timedelta(days=7))
        elif self.method.lower() == 'past':
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
            self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            raise ValueError
        self.urls = (f'https://www.livescore.com/soccer/{(self.start_date + timedelta(day)).strftime("%Y-%m-%d")}'
                     for day in range(int((self.end_date - self.start_date).days)))
        self.options = webdriver.ChromeOptions()
        self.options.headless = True
        self.driver = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver.exe'), options=self.options)
        self.data = pd.DataFrame()

    def scrape(self):
        # TODO: Try Except Value Error Finally driver.close()
        for url in self.urls:
            self.driver.get(url)
            self.driver.execute_script("window.scrollBy(0,10000);")
            self.driver.execute_script("window.scrollBy(0,10000);")
            self.driver.execute_script("window.scrollBy(0,10000);")
            self.driver.execute_script("window.scrollBy(0,10000);")
            self.driver.execute_script("window.scrollBy(0,10000);")
            home_team = [element.text for element in
                         self.driver.find_elements_by_xpath('//div[@class="ply tright name"]')]
            away_team = [element.text for element in
                         self.driver.find_elements_by_xpath('//div[@class="ply name"]')]
            date = [url[33:len(url)] for _ in home_team]
            if self.method.lower() == 'past':
                home_score = [element.text for element in
                              self.driver.find_elements_by_xpath('//span[@class="hom"]')]
                away_score = [element.text for element in
                              self.driver.find_elements_by_xpath('//span[@class="awy"]')]
                new_data = pd.DataFrame({'date': date, 'homeTeam': home_team, 'awayTeam': away_team,
                                         'homeTeamFt': home_score, 'awayTeamFt': away_score})
                if 'livescore' not in os.listdir(os.path.join(os.getcwd(), 'data')):
                    os.mkdir('data/livescore')
                new_data.to_csv(f'data/livescore/{url[33:len(url)]}.csv', encoding='utf-8')
                print(url[33:len(url)])
                if not self.data.empty:
                    self.data = pd.concat([self.data, new_data])
                else:
                    self.data = self.data.append(new_data, ignore_index=True)
            elif self.method.lower() == 'upcoming':
                new_data = pd.DataFrame({'date': date, 'homeTeam': home_team, 'awayTeam': away_team})
                if not self.data.empty:
                    self.data = pd.concat([self.data, new_data])
                else:
                    self.data = self.data.append(new_data, ignore_index=True)
                print(new_data)
        self.driver.close()
        self.data = self.data.reset_index().drop('index', axis=1)[:-1]
        return self

    def export(self):
        if self.method.lower() == 'upcoming':
            self.data.to_csv('data/upcoming.csv')
        if self.method.lower() == 'past':
            self.data.to_csv('data/database.csv')
        return self


if __name__ == "__main__":
    # scraper = Scraper('2020-07-29', '2020-07-30')
    scraper = Scraper('past', '2019-08-02', '2020-08-01')
    scraper.scrape()
    print(scraper.data)
