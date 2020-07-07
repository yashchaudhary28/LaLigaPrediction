from dataCleaning import avg, new_season, hist_pair
import pandas as pd
import numpy as np
from collections import Counter
import concurrent.futures
import time

t1 = time.perf_counter()
#For removing the SettingsWithCopyWarning, which says we are using copy istead of the orginal file.
pd.options.mode.chained_assignment = None
hist_pair.reset_index(inplace = True)

#Function to find result
#From scoreline who wins the match H (Home), A(Away) or D(Draw)
def result_calculator(h_goal, a_goal):
    if h_goal == a_goal:
        return 'D'
    elif h_goal > a_goal:
        return 'H'
    else:
        return 'A'
#Function to calibrate results.
#if the probablity of winning of home and away is tight
#it should be considered as a draw.
def result_calibrate(prob_h, prob_d, prob_a):
    if abs(prob_h - prob_a) < 0.01:
        return 'D'
    elif prob_h == max(prob_d, prob_h, prob_a):
        return 'H'
    elif prob_d == max(prob_d, prob_h, prob_a):
        return 'D'
    else:
        return 'A'

#get most frequent score line of a match
def get_score(Home, Away, nsim):
    pair = hist_pair[(hist_pair['HomeTeam'] == Home) & (hist_pair['AwayTeam'] == Away)]
    pair.reset_index(inplace = True)
    pair.drop('index', axis = 1, inplace = True)
    avg_home_scored = pair.avg_home_scored_ft
    avg_away_scored = pair.avg_away_scored_ft

    avg_Home = avg[avg['Team'] == Home].reset_index(drop = True)
    avg_Away = avg[avg['Team'] == Away].reset_index(drop = True)
    total_avg_home_scored = avg_Home.loc[0, 'avg_scored_ft_h']
    total_avg_away_scored = avg_Away.loc[0,'avg_scored_ft_a']
    total_avg_away_conceded = avg_Away.loc[0,'avg_conceded_ft_a']
    total_avg_home_conceded = avg_Home.loc[0,'avg_conceded_ft_h']
    result = []
    for i in range(0,nsim+1):
        if (pair.shape[0] == 1):
            #if we have no historical result of the matches
            if(pair.loc[0].Matches > 3):
                home_scored = np.random.poisson(avg_home_scored, 1)
                away_scored = np.random.poisson(avg_away_scored, 1)
            else:
                #take into account both attacking stat at home and defence stat away.
                home_scored = np.random.poisson(0.5 * (total_avg_home_scored + total_avg_away_conceded), 1)
                away_scored = np.random.poisson(0.5 * (total_avg_away_scored + total_avg_home_conceded), 1)
        else:
            #take into account both attacking stat at home and defence stat away.
            home_scored = np.random.poisson(0.5 * (total_avg_home_scored + total_avg_away_conceded), 1)
            away_scored = np.random.poisson(0.5 * (total_avg_away_scored + total_avg_home_conceded), 1)
        result.append(result_calculator(home_scored, away_scored))
    lst = list(Counter(result).values())
    final_values = list(np.divide(lst, nsim))
    lst_keys = list(Counter(result).keys())
    matches.append(dict(zip(lst_keys, final_values)))

nsim = 10000
ziped = list(zip(list(new_season.HomeTeam), list(new_season.AwayTeam)))
# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor:
    for x,y in ziped:
        future_to_dict = executor.submit(get_score,x,y,nsim)

new_season['H'] = [match.get('H') for match in matches]
new_season['A'] = [match.get('A') for match in matches]
new_season['D'] = [match.get('D') for match in matches]
new_season['prediction'] = new_season.apply(lambda row: result_calibrate(row['H'], row['D'], row['A']), axis = 1)
t2 = time.perf_counter()

new_season.to_csv("prediction.csv", index = True)
print(f'Finished in {t2-t1} seconds')
