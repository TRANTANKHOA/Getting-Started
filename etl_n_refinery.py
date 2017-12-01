# Raw data
import pandas as pd

historical_data_link = "nfl_historical_data.csv"
dataframe = pd.read_csv(historical_data_link)
dataframe.tail(10)
dataframe.describe()

# detail profiling
import pandas_profiling as profiler
import webbrowser as browser
import os

html = historical_data_link + ".profile.html"
profiler.ProfileReport(dataframe).to_file(html)
browser.open('file://' + os.path.realpath(html))

# clean and transform
dataframe.rename(index=str, columns={
    "team_1_name": "home_team",
    "team_1_score": "home_score",
    "team_2_name": "guess_team",
    "team_2_score": "guess_score"
}, inplace=True)
dataframe['time_stamp'] = pd.to_datetime(dataframe.date)
dataframe.drop(['id', 'date'], axis=1, inplace=True)
dataframe['year'], \
dataframe['month'], \
dataframe['day'], \
dataframe['hour'] = \
    dataframe.time_stamp.dt.year, \
    dataframe.time_stamp.dt.month, \
    dataframe.time_stamp.dt.day, \
    dataframe.time_stamp.dt.hour
dataframe.dtypes # show schema
all_teams = dataframe['home_team'].values

#  linear regression
from sklearn import linear_model

regr = linear_model.LinearRegression()
import numpy as np

numArray = np.asarray(dataframe)
features = numArray[:, ]
regr.fit()
