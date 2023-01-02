from fmlib import etl, metrics
import fmlib.smarkets_client as client

import pandas as pd
import numpy as np
import datetime as dt

from logging.config import fileConfig
from pprint import pprint

import warnings
warnings.filterwarnings('ignore')

# UNDERSTAT
season = '2022'
league = 'EPL'  # English Premier League

dte = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

all_fixtures = pd.DataFrame(etl.get_upcoming_fixtures(league, season))[['h', 'a', 'datetime']]
upcoming_fixtures = all_fixtures[all_fixtures['datetime'] >= dte].head(10)

for h_a in ['h', 'a']:
    upcoming_fixtures[h_a] = [x['title'] for x in upcoming_fixtures[h_a]]

i = 0

home_team = upcoming_fixtures['h'].iloc[i]
away_team = upcoming_fixtures['a'].iloc[i]

# fetch league Home & Away XG table
dfs = etl.get_league_tables(league, season)

# allocate and reformat dataframes
home_df, away_df = etl.format_understat_data(dfs)

# split 2 dataframes for home and away realised goals scored/conceded
home_xg = etl.expected_goals_df(home_df)
away_xg = etl.expected_goals_df(away_df)

# away team
avg_away_gpg_scored_away = metrics.away_team_gpg_scored_away(away_team, away_xg)
avg_away_gpg_conceded_away = metrics.away_team_gpg_conceded_away(away_team, away_xg)

# home team
avg_home_gpg_scored_home = metrics.home_team_gpg_scored_at_home(home_team, home_xg)
avg_home_gpg_conceded_home = metrics.home_team_gpg_conceded_at_home(home_team, home_xg)

# total averages
total_avg_home_gpg_scored = home_xg['GpG_Scored'].mean()
total_avg_away_gpg_scored = away_xg['GpG_Scored'].mean()

# Team average goals scored & conceded as ratios of the total league averages
home_attack = avg_home_gpg_scored_home / total_avg_home_gpg_scored
home_defence = avg_home_gpg_conceded_home / total_avg_away_gpg_scored
away_attack = avg_away_gpg_scored_away / total_avg_away_gpg_scored
away_defence = avg_away_gpg_conceded_away / total_avg_home_gpg_scored

projected_home_goals = total_avg_home_gpg_scored * home_attack * away_defence  # Home goals scored in fixture
projected_away_goals = total_avg_away_gpg_scored * away_attack * home_defence  # Away goals scored in fixture
projected_total_goals = projected_away_goals + projected_home_goals  # Total goals in fixture

k = 25

# Home goals probability
home_goals_probabilities = []
away_goals_probabilities = []
for i in range(k):
    home_goals_probabilities.append(metrics.poisson(k=i, lam=projected_home_goals))
    away_goals_probabilities.append(metrics.poisson(k=i, lam=projected_away_goals))

# Result probability matrix
probability_matrix = pd.DataFrame(0, columns=home_goals_probabilities, index=away_goals_probabilities)
for i in probability_matrix.columns:
    for j in probability_matrix.index:
        probability_matrix.loc[j, i] = i * j

home_win_probability = np.triu(probability_matrix.to_numpy()).sum() - probability_matrix.to_numpy().trace()
draw_probability = probability_matrix.to_numpy().trace()
away_win_probability = np.tril(probability_matrix.to_numpy()).sum() - probability_matrix.to_numpy().trace()

np.testing.assert_almost_equal(home_win_probability + away_win_probability + draw_probability, 1, decimal=2)

home_implied_odds = 1 / home_win_probability
draw_implied_odds = 1 / draw_probability
away_implied_odds = 1 / away_win_probability

# over goals
goals_0_5 = 1 - probability_matrix.iloc[0, 0]
goals_1_5 = 1 - sum([probability_matrix.iloc[0, 0], probability_matrix.iloc[1, 0], probability_matrix.iloc[0, 1]])

print(f"Fixture: {home_team} vs. {away_team}")
print("============================================")
print(f"Probability of {home_team} Win: {home_win_probability:.2f}")
print(f"Probability of Draw: {draw_probability:.2f}")
print(f"Probability of {away_team} Win: {away_win_probability:.2f}")
print("============================================")
print(f"IO of {home_team} Win: {home_implied_odds:.2f}")
print(f"IO of Draw: {draw_implied_odds:.2f}")
print(f"IO of {away_team} Win: {away_implied_odds:.2f}")
print("============================================\nGoals Over Market")
print("Goals | Probability | IO")
print(f"0.5 | {goals_0_5:.2f} | {(1 / goals_0_5):.2f}")

# SMARKETS
fileConfig('logging.config', disable_existing_loggers=False)

# instantiate client: single instance per session
# copy the template from configuration_template.toml and fill it with
# your credentials!
client = client.SmarketsClient()

# do initial authentication
client.init_session()

# date for events
start_date = dt.datetime.now() + dt.timedelta(days=1)

events = client.get_available_events(['upcoming'], ['football_match'], start_date, 20)

# place some bets
"""
client.place_order(
    market_id,    # market id
    contract_id,  # contract id
    50,           # percentage price * 10**4, here: 0.5% / 200 decimal / 19900 american
    500000,       # quantity: total stake * 10**4, here: 50 GBP. Your buy order locks 0.25 GBP, as
                  #      0.25 GBP * 200 = 50 GBP
    'buy',        # order side: buy or sell
)
"""

# lets get the orders now!
pprint(client.get_orders(states=['created', 'filled', 'partial']))

pprint(client.get_accounts())

# eeh, changed my mind
# client.cancel_order('202547466272702478')
