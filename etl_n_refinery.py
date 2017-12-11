# Raw data
import pandas as pd

historical_data_link = "nba_historical_data.csv"
dataframe = pd.read_csv(historical_data_link)
dataframe.tail(10)
dataframe.describe()

# detail profiling
import pandas_profiling as profiler
import webbrowser as browser
import os


def show_profile(dataframe):
    html = historical_data_link + ".profile.html"
    profiler.ProfileReport(dataframe).to_file(html)
    browser.open('file://' + os.path.realpath(html))
    return


show_profile(dataframe)
# clean and transform
home_team, home_score = 'home_team', 'home_score'
guess_team, guess_score = 'guess_team', 'guess_score'
year, month, day, hour = 'year', 'month', 'day', 'hour'
dataframe.rename(index=str, columns={
    "team_1_name": home_team,
    "team_1_score": home_score,
    "team_2_name": guess_team,
    "team_2_score": guess_score
}, inplace=True)
dataframe['time_stamp'] = pd.to_datetime(dataframe.date)
dataframe.drop(['id', 'date'], axis=1, inplace=True)
dataframe[year], \
dataframe[month], \
dataframe[day], \
dataframe[hour] = \
    dataframe.time_stamp.dt.year, \
    dataframe.time_stamp.dt.month, \
    dataframe.time_stamp.dt.day, \
    dataframe.time_stamp.dt.hour
show_profile(dataframe)

# create a table of features for each team
is_home, opponent, score, gain, match_count, mean_gain, min_gain, max_gain, sigma_gain, mean_score, min_score, max_score, sigma_score = \
    'is_home', 'opponent', 'score', 'gain', 'match_count', 'mean_gain', 'min_gain', 'max_gain', 'sigma_gain', 'mean_score', 'min_score', 'max_score', 'sigma_score'

all_teams = pd.unique(dataframe[[home_team, guess_team]].values.ravel('K'))


def build_profile(team):
    print("Start with", team)
    filtered_df = dataframe[
        (dataframe[home_team] == team) | (dataframe[guess_team] == team)
        ]

    filtered_df[is_home] = filtered_df.apply(func=lambda row: row.home_team == team, axis=1)
    filtered_df[opponent] = filtered_df.apply(
        func=lambda row:
        row.guess_team if row.is_home
        else row.home_team, axis=1
    )
    filtered_df[score] = filtered_df.apply(
        func=lambda row:
        row.home_score if row.is_home
        else row.guess_score, axis=1
    )
    filtered_df[gain] = filtered_df.apply(
        func=lambda row: row.score - (row.guess_score if row.is_home else row.home_score), axis=1
    )

    def previous_rows_with_same_opponent(row): return filtered_df[
        (filtered_df.opponent == row.opponent) & (filtered_df.time_stamp < row.time_stamp)
        ]

    def previous_vals_with_same_opponent(row, column): return previous_rows_with_same_opponent(row)[column]

    filtered_df[match_count] = filtered_df.apply(
        func=lambda row: previous_rows_with_same_opponent(row).shape[0], axis=1
    )

    filtered_df[mean_gain] = filtered_df.apply(
        func=lambda row: previous_vals_with_same_opponent(row, gain).mean(), axis=1
    ).fillna(0)

    filtered_df[min_gain] = filtered_df.apply(
        func=lambda row: previous_vals_with_same_opponent(row, gain).min(), axis=1
    ).fillna(0)

    filtered_df[max_gain] = filtered_df.apply(
        func=lambda row: previous_vals_with_same_opponent(row, gain).max(), axis=1
    ).fillna(0)

    import math
    filtered_df[sigma_gain] = filtered_df.apply(
        func=lambda row: math.sqrt(previous_vals_with_same_opponent(row, gain).var()), axis=1
    ).fillna(0)

    filtered_df[mean_score] = filtered_df.apply(
        func=lambda row: previous_vals_with_same_opponent(row, score).mean(), axis=1
    ).fillna(0)

    filtered_df[min_score] = filtered_df.apply(
        func=lambda row: previous_vals_with_same_opponent(row, score).min(), axis=1
    ).fillna(0)

    filtered_df[max_score] = filtered_df.apply(
        func=lambda row: previous_vals_with_same_opponent(row, score).max(), axis=1
    ).fillna(0)

    filtered_df[sigma_score] = filtered_df.apply(
        func=lambda row: math.sqrt(previous_vals_with_same_opponent(row, score).var()), axis=1
    ).fillna(0)

    filtered_df.drop([home_team, home_score, guess_team, guess_score], axis=1, inplace=True)

    print("End with", team)
    return filtered_df.sort_values([opponent, match_count], ascending=[True, True])


chicago = build_profile('Chicago Bulls')
chicago.tail()
chicago.plot(kind='scatter', x='d_ability_1', y='score')
chicago.groupby(opponent).gain.agg(['min', 'max', 'mean'])['mean'].plot()

show_profile(chicago)

teams_profiles = [build_profile(team) for team in all_teams]

# linear regression
from sklearn import linear_model

regr = linear_model.LinearRegression()

import numpy as np

numArray = np.asarray(dataframe)

features = numArray[:, ]
regr.fit()
