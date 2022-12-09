from understat import Understat
from pandas import DataFrame

import asyncio
import aiohttp


def get_league_tables(league: str, season: str) -> list:
    async def main():
        async with aiohttp.ClientSession() as session:
            understat = Understat(session)
            home_table = await understat.get_league_table(league, season, h_a='h')
            away_table = await understat.get_league_table(league, season, h_a='a')
        return [DataFrame(home_table), DataFrame(away_table)]

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(main())


def format_understat_data(dfs: list) -> list:
    """
    Returns understat league tables raw data as appropriately formatted pandas DataFrames
    :param dfs: understat league tables
    :return: original DataFrames with appropriate formatting
    """
    for i in range(len(dfs)):
        header_row = dfs[i].iloc[0]
        dfs[i].columns = header_row
        dfs[i] = dfs[i].drop(dfs[i].index[0])
        dfs[i].reset_index(inplace=True, drop=True)
        req_columns = [
            'Team', 'M', 'W', 'D', 'L', 'G', 'GA',
            'PTS', 'xG', 'NPxG', 'xGA', 'NPxGA',
            'NPxGD', 'PPDA', 'OPPDA', 'DC', 'ODC', 'xPTS'
        ]
        assert (len(dfs[i]) == 20) and (dfs[i].columns == req_columns).all(), "Error occured when loading table"

    return dfs


def realised_goals_df(df: DataFrame) -> DataFrame:
    """
    Reformats raw league table DataFrame as a realised goals table
    :param df: league table
    :return: new league table stripped of irrelevant columns and appended with additional metric columns
    """
    new_df = df[['Team', 'M', 'W', 'D', 'L', 'G', 'GA', 'PTS']]

    new_df['GpG_Scored'] = new_df.iloc[:, 5] / new_df.iloc[:, 1]
    new_df['GpG_Conceded'] = new_df.iloc[:, 6] / new_df.iloc[:, 1]

    return new_df


def expected_goals_df(df: DataFrame) -> DataFrame:
    """
    Reformats raw league table DataFrame as an expected goals table
    :param df: league table
    :return: new league table stripped of irrelevant columns and appended with additional metric columns
    """
    new_df = df[['Team', 'M', 'W', 'D', 'L', 'xG', 'xGA', 'xPTS']]

    new_df['GpG_Scored'] = new_df.iloc[:, 5] / new_df.iloc[:, 1]
    new_df['GpG_Conceded'] = new_df.iloc[:, 6] / new_df.iloc[:, 1]

    return new_df
