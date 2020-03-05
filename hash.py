import pandas as pd
import os, string

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

scores = open(os.path.join(__location__, 'Scores.csv'), 'r', encoding='Windows-1250')
df_scores = pd.read_csv(scores, delimiter=',')

match_dates = df_scores['Date'].tolist()
home_team = df_scores['HomeT'].tolist()
away_team = df_scores['AwayT'].tolist()
home_score = df_scores['HomeS'].tolist()
away_score = df_scores['AwayS'].tolist()

unique_teams = set()

for home, away in zip(home_team, away_team):
    unique_teams.add(home)
    unique_teams.add(away)

unique_teams = sorted(unique_teams)
unique_codes = range(1, len(unique_teams) + 1)

code_home = []
code_away = []

for h, a in zip(home_team, away_team):
    code_home.append(unique_codes[unique_teams.index(h)])
    code_away.append(unique_codes[unique_teams.index(a)])

df = pd.DataFrame({'Date': match_dates,
                   'Home Team': home_team, 'Home Team Code': code_home,
                   'Away Team': away_team, 'Away Team Code': code_away,
                   'Home Score': home_score, 'Away Score': away_score})

writer = pd.ExcelWriter(os.path.join(__location__, 'match history.xlsx'), engine='xlsxwriter')

df.to_excel(writer, sheet_name='Database')

writer.save()

team_codes = open(os.path.join(__location__, 'codes.csv'), 'w', encoding='Windows-1250')
team_codes.write('Team' + ',' + 'Code' + '\n')
for team, code in zip(unique_teams, unique_codes):
    team_codes.write(team + ',' + str(code) + '\n')
team_codes.close()