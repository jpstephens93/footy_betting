from fmlib import etl, metrics

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')

season = '2022'
league = 'EPL'  # English Premier League

home_team = 'Arsenal'
away_team = 'Aston Villa'

# fetch league Home & Away XG table
dfs = etl.get_league_tables(league, season)

# allocate and reformat dataframes
home_df, away_df = etl.format_understat_data(dfs)

# split 2 dataframes for home and away realised goals scored/conceded
home_realised_g = etl.realised_goals_df(home_df)
away_realised_g = etl.realised_goals_df(away_df)


avg_away_gpg_scored_away = metrics.expected_away_team_gpg_scored_away(away_team)
avg_away_gpg_conceded_away = away_realised_g[away_realised_g['Team'] == away_team]['GpG_Conceded'].iloc[0]

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
