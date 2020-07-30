from flask import Flask, make_response, render_template
import pandas as pd

app = Flask(__name__)

data = pd.read_csv("data/dataset.csv", index_col=0)


@app.route('/', methods=['GET'])
def home():
    return render_template(template_name_or_list='templates/index.html')


@app.route("/stats/<team>/<location>", methods=['GET'])
def team_stats(team, location):
    if location.lower() == 'all':
        return data[(data['homeTeam'] == team) | (data['awayTeam'] == team)].to_html()
    if location.lower() == 'home':
        return data[data['homeTeam'] == team].to_html()
    if location.lower() == 'away':
        return data[data['awayTeam'] == team].to_html()


@app.route("/download/<team>/<location>", methods=['GET'])
def download_stats(team, location):
    if location.lower() == 'all':
        response = make_response(data[data['homeTeam'] == team].to_csv())
        response.headers["Content-Disposition"] = f"attachment; filename={team} {location}.csv"
        response.headers["Content-Type"] = "text/csv"
        return response,
    if location.lower() == 'home':
        response = make_response(data[(data['homeTeam'] == team) | (data['awayTeam'] == team)].to_csv())
        response.headers["Content-Disposition"] = f"attachment; filename={team} {location}.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    if location.lower() == 'away':
        response = make_response(data[data['awayTeam'] == team].to_csv())
        response.headers["Content-Disposition"] = f"attachment; filename={team} {location}.csv"
        response.headers["Content-Type"] = "text/csv"
        return response


if __name__ == '__main__':
    app.run()
