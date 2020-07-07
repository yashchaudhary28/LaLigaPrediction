from dataCleaning import avg, new_season, hist_pair
import pandas as pd
import numpy as np
from collections import Counter

#For removing the SettingsWithCopyWarning, which says we are using copy istead of the orginal file.
pd.options.mode.chained_assignment = None
hist_pair.reset_index(inplace = True)

def get_score(Home, Away):
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
    return home_scored, away_scored

def rank_team(m_result):
    name = avg.Team
    goal_score = [0] * 20
    goal_conceded = [0] * 20
    point = [0] * 20
    table = pd.DataFrame(list(zip(name, goal_score, goal_conceded, point)), columns = ["Name", 'goal_score', 'goal_conceded', 'point'])
    for i in range(1:nrow(m_result)):
        home = m_result.HomeTeam[i]
        away = m_result.AwayTeam[i]
        home_goal = m_result.home_scored[i]
        away_goal = m_result.away_scored[i]
        #add goal
        table.loc[table['Name'] == home, ['goal_score']] = (table[table.Name == home].goal_score) + home_goal
        table.loc[table['Name'] == home, ['goal_conceded']] = (table[table.Name == home].goal_conceded) + away_goal
        table.loc[table['Name'] == away, ['goal_score']] = (table[table.Name == away].goal_score) + away_goal
        table.loc[table['Name'] == away, ['goal_conceded']] = (table[table.Name == away].goal_conceded) + home_goal

        #calculate point
        if (home_goal > away_goal):
            table.loc[table['Name'] == home, ['point']] = (table[table.Name == home].point) + 3
        elif home_goal < away_goal :
            table.loc[table['Name'] == away, ['point']] = (table[table.Name == away].point) + 3
        else:
            table.loc[table['Name'] == home, ['point']] = (table[table.Name == home].point) + 1
            table.loc[table['Name'] == away, ['point']] = (table[table.Name == away].point) + 1

    table[goal_difference] = table['goal_score'] - table['goal_conceded']
    table = table.sort_values(by = ['3', '4', '1'], ascending = False)
    return table

def simulate(fixtures):
    matches =
