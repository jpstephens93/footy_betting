import math
from pandas import DataFrame


def total_expected_home_gpg_scored(home_realised_g_data: DataFrame) -> float:
    """
    Expected/mean/average home GpG scored
    :param home_realised_g_data: pandas DataFrame of home realised goals data table
    :return: statistical mean of GpG scored
    """
    return home_realised_g_data['GpG_Scored'].mean()


def total_expected_away_gpg_scored(away_realised_g_data: DataFrame) -> float:
    """
    Expected/mean/average away GpG scored
    :param away_realised_g_data: pandas DataFrame of away realised goals data table
    :return: statistical mean of GpG scored
    """
    return away_realised_g_data['GpG_Scored'].mean()


def home_team_gpg_scored_at_home(home_team: str, home_realised_g_data: DataFrame) -> float:
    """
    Looks up the home team GpG scored at home from the home realised goals data
    :param home_team: Name of the home team
    :param home_realised_g_data: DataFrame containing home realised goals data
    :return: float of home team GpG scored at home
    """
    return home_realised_g_data[home_realised_g_data['Team'] == home_team]['GpG_Scored'].iloc[0]


def home_team_gpg_conceded_at_home(home_team: str, home_realised_g_data: DataFrame) -> float:
    """
    Looks up the home team GpG conceded at home from the home realised goals data
    :param home_team: Name of the home team
    :param home_realised_g_data: DataFrame containing home realised goals data
    :return: float of home team GpG conceded at home
    """
    return home_realised_g_data[home_realised_g_data['Team'] == home_team]['GpG_Conceded'].iloc[0]


def away_team_gpg_scored_away(away_team: str, away_realised_g_data: DataFrame) -> float:
    """
    Looks up the away team GpG scored away from the away realised goals data
    :param away_team: Name of the away team
    :param away_realised_g_data: DataFrame containing away realised goals data
    :return: float of away team GpG scored away
    """
    return away_realised_g_data[away_realised_g_data['Team'] == away_team]['GpG_Scored'].iloc[0]


def away_team_gpg_conceded_away(away_team: str, away_realised_g_data: DataFrame) -> float:
    """
    Looks up the away team GpG conceded away from the away realised goals data
    :param away_team: Name of the away team
    :param away_realised_g_data: DataFrame containing away realised goals data
    :return: float of away team GpG conceded away
    """
    return away_realised_g_data[away_realised_g_data['Team'] == away_team]['GpG_Conceded'].iloc[0]


def poisson(k, lam):
    """
    Formula for the poisson distribution given some k and lam values
    :param k: Poisson random variable
    :param lam: Average rate of value (i.e. expected goals)
    :return: float value of event probability
    """
    return (lam ** k * math.e ** -lam) / math.factorial(k)
