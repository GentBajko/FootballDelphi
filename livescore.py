from bs4 import BeautifulSoup
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

yesterday = date.today() - timedelta(days=1)
start_date = date(int(input('Enter Year: ')), int(input('Enter Month: ')), int(input('Enter Day: ')))
end_date = date.today()

for single_date in daterange(start_date, end_date):
    date = str(single_date)
    print(date)
    url = 'https://www.livescore.com/soccer/' + date
    
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(os.path.join(__location__, 'chromedriver.exe'), options=options)
    driver.get(url)
    driver.set_page_load_timeout(10)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    home = soup.find_all('div', class_='ply tright name')
    away = soup.find_all('div', class_='ply name')
    hScore = soup.find_all('span', class_='hom')
    aScore = soup.find_all('span', class_='awy')

    with open(os.path.join(__location__, 'Scores.csv'), 'a') as f:
        for h, a, hs, aws in zip(home, away, hScore, aScore):
            if h.text == '__home_team__' or hs.text == '?':
                pass
            else:
                try:
                    f.write(date + ',' + h.text.replace(' *', '') + ',' + hs.text + ',' + a.text.replace(' *', '') + ',' + aws.text + '\n')
                except UnicodeEncodeError:
                    print('Program crashed. Please check the last date extracted and then restart')
                    pass
        driver.close()

