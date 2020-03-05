import pandas as pd
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

scores = open(os.path.join(__location__, 'Scores.csv'), 'r', encoding='Windows-1250')
df_scores = pd.read_csv(scores, delimiter=',')

match_dates = df_scores['Date'].tolist()
home_team = df_scores['HomeT'].tolist()
away_team = df_scores['AwayT'].tolist()
home_score = df_scores['HomeS'].tolist()
away_score = df_scores['AwayS'].tolist()

df = pd.DataFrame({'Date': match_dates,
                   'Home Team': home_team, 'Away Team': away_team,
                   'Home Score': home_score, 'Away Score': away_score
                   })

writer = pd.ExcelWriter(os.path.join(__location__, 'match history.xlsx'), engine='xlsxwriter')

df.to_excel(writer, sheet_name='Database')

writer.save()