import pandas as pd

#importing the required datasets
history = pd.read_csv("C:\\Users\\yashc\\Desktop\\workspace\\LaLigaPrediction\\Data\\history.csv")
fixtures = pd.read_csv("C:\\Users\\yashc\\Desktop\\workspace\\LaLigaPrediction\\Data\\fixtures.csv")
latest = pd.read_csv("C:\\Users\\yashc\\Desktop\\workspace\\LaLigaPrediction\\Data\\2019-2020.csv")

#Finding team names
teams = fixtures.Home.unique()
teams = list(teams)
teams_name = latest.HomeTeam.unique()
teams_name = list(teams_name)
history = history[history.HomeTeam.isin(teams_name)]
history = history[history.AwayTeam.isin(teams_name)]
#as we have gathered data from different places so team names don't match.
dict = {}
for key in teams:
    for value in teams_name:
        dict[key] = value
        teams_name.remove(value)
        break
#Fixing the team names problem.
fixtures = fixtures.replace(dict)
#datatypes of history dataframe
history.dtypes
#converting the season datatype from int64 to str.
history['Season'] = history['Season'].astype(str)

#Average home dataframe team wise.
avg_home = history.groupby('HomeTeam').mean()
avg_home.rename(columns = {'HomeTeam':'Team','FTHG':'avg_scored_ft_h','FTAG':'avg_conceded_ft_h','HTHG':'avg_scored_ht_h','HTAG':'avg_conceded_ht_h'}, inplace = True)

#Average away dataframe team wise
avg_away = history.groupby('AwayTeam').mean()
avg_away.rename(columns = {'AwayTeam':'Team','FTHG':'avg_conceded_ft_a','FTAG':'avg_scored_ft_a','HTHG':'avg_conceded_ht_a','HTAG':'avg_scored_ht_a'}, inplace = True)

#merge the average datasets(avg_away, avg_home)
avg = pd.merge(avg_home, avg_away, left_index = True, right_index = True) #Final 1
avg.reset_index(inplace = True)
avg.rename(columns = {'HomeTeam':'Team'}, inplace = True)

#Pair wise
hist_pair_mean = history.groupby(['HomeTeam', 'AwayTeam']).mean()
hist_pair_count = history.groupby(['HomeTeam', 'AwayTeam'])['Date'].count()
hist_pair = hist_pair_mean.merge(hist_pair_count, how = 'outer', left_index = True, right_index = True)
hist_pair.rename(columns = {'FTHG':'avg_home_scored_ft','FTAG':'avg_away_scored_ft','HTHG':'avg_home_scored_ht','HTAG':'avg_away_scored_ht', 'Date':'Matches'}, inplace = True)

new_season = fixtures.rename(columns = {'Home': 'HomeTeam', 'Away': 'AwayTeam'})

hist_pair.to_csv( "hist_pair.csv", index=True, encoding='utf-8-sig')
#clean data from memory
del avg_away, avg_home, history, fixtures, teams, teams_name, latest
