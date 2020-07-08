from dataCleaning import avg, new_season, hist_pair
import pandas as pd
import numpy as np

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
    return [home_scored, away_scored]

def rank_team(m_result):
    name = avg.Team
    goal_score = [0] * 20
    goal_conceded = [0] * 20
    point = [0] * 20
    table = pd.DataFrame(list(zip(name, goal_score, goal_conceded, point)), columns = ["Name", 'goal_score', 'goal_conceded', 'point'])
    for i in range(0,len(m_result.index)):
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

    table['goal_difference'] = table['goal_score'] - table['goal_conceded']
    table = table.sort_values(by = ['point', 'goal_difference', 'goal_score'],ascending = False)
    return table

def simulate(fixtures):
    matches = map(get_score, fixtures.HomeTeam, fixtures.AwayTeam)
    fixtures['home_scored'] = [match[0] for match in matches]
    matches_1 = map(get_score, fixtures.HomeTeam, fixtures.AwayTeam)
    fixtures['away_scored'] = [match[1] for match in matches_1]
    table = rank_team(fixtures)
    return table

nsim = 1000
name = avg.Team
champion = [0] * 20
runner_up = [0] * 20
top_4 = [0] * 20
top_6 = [0] * 20
relegate = [0] * 20
tabulate_data = pd.DataFrame(list(zip(name, champion, runner_up, top_4, top_6, relegate)), columns = ["Name", 'Champion', 'Runner_Up', 'Top_4', 'Top_6', 'Relegate'])

for sim in range(0, nsim):
    table_final = simulate(new_season)
    table_final.reset_index(inplace = True)

    first = table_final.Name[0]
    second = table_final.Name[1]
    first_4 = list(table_final.Name[0:4])
    first_6 = list(table_final.Name[0:6])
    last_3 = list(table_final.Name[17:20])

    tabulate_data['Champion'] = np.where((tabulate_data.Name == first), tabulate_data.Champion + 1, tabulate_data.Champion)
    tabulate_data['Runner_Up'] = np.where((tabulate_data.Name == second), tabulate_data.Runner_Up + 1, tabulate_data.Runner_Up)
    for i, row in tabulate_data.iterrows():
        if row['Name'] in first_4:
            tabulate_data.loc[i,'Top_4'] = row['Top_4'] + 1
        if row['Name'] in first_6:
            tabulate_data.loc[i,'Top_6'] = row['Top_6'] + 1
        if row['Name'] in last_3:
            tabulate_data.loc[i,'Relegate'] = row['Relegate'] + 1
#Convert to percentage
tabulate_data = tabulate_data.assign(Champion = tabulate_data.Champion / nsim,
                                    Runner_Up = tabulate_data.Runner_Up / nsim,
                                    Top_4 = tabulate_data.Top_4 / nsim,
                                    Top_6 = tabulate_data.Top_6 / nsim,
                                    Relegate = tabulate_data.Relegate / nsim)

tabulate_data.to_csv("final_result.csv", index = False)
