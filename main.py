from fmlib import etl, metrics

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

season = '2022'
league = 'EPL'  # English Premier League

home_team = 'Aston Villa'
away_team = 'Liverpool'

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

if __name__ == '__main__':
    print(f"Fixture: {home_team} vs. {away_team}")
    print("============================================")
    print(f"Probability of {home_team} Win: {home_win_probability:.2f}")
    print(f"Probability of Draw: {draw_probability:.2f}")
    print(f"Probability of {away_team} Win: {away_win_probability:.2f}")
    print("============================================")
    print(f"IO of {home_team} Win: {home_implied_odds:.2f}")
    print(f"IO of Draw: {draw_implied_odds:.2f}")
    print(f"IO of {away_team} Win: {away_implied_odds:.2f}")
