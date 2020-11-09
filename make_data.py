#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 21:10:03 2020

@author: Nick Clifford
"""
#%% Setup

import pandas as pd
import numpy as np
pd.options.display.max_columns = 20

datadir = '/Users/nickclifford/Documents/UVA/Spring 2020/SYS 6016 Machine Learning/final_proj/data'

#%% Team data

# read in team data
bask = pd.read_csv(datadir + '/updated_bask_data2.csv', parse_dates=['date'])

# remove playoff season games, reset index
bask = bask[pd.isnull(bask.playoff)]
bask.index = range(len(bask))

# drop playoff, elo_pre, and score columns
bask = bask.drop(['playoff', 'elo1_pre', 'elo2_pre', 'score1', 'score2'], axis=1)

# convert home/away team cols to a binary col for home for the team of interest
bask['home'] = pd.Series(np.where(bask['team1..Home.'] == bask.team_of_interest, 1, 0))

# rename team_of_interest to team
bask = bask.rename({'team_of_interest':'team'}, axis=1)


#%% All-star data

# read in all-star data
stars = pd.read_excel(datadir + '/All Star List.xlsx')

# turn every 4 columns into df, remove NaN values from each, rename columns to same heading, add a date column for year of all-star game
df16 = stars.iloc[:-2,:4].rename({'2015 2016 All Stars': 'player', 'Team':'team', 'Starter?':'starter', 'Age':'age'}, axis=1)
df16['season'] = 2016

df17 = stars.iloc[:-2,4:8].rename({'2016 2017 All Stars': 'player', 'Team.1':'team', 'Starter?.1':'starter', 'Age.1':'age'}, axis=1)
df17['season'] = 2017

df18 = stars.iloc[:-3,8:12].rename({'2017 2018 All Stars': 'player', 'Team.2':'team', 'Starter?.2':'starter', 'Age.2':'age'}, axis=1)
df18['season'] = 2018

df19 = stars.iloc[:,12:16].rename({'2018 2019 All Stars': 'player', 'Team.3':'team', 'Starter? ':'starter', 'Age.3':'age'}, axis=1)
df19['season'] = 2019

df20 = stars.iloc[:-2,16:20].rename({'2019 2020 All Stars': 'player', 'Team.4':'team', 'Starter?.3':'starter', 'Age.4':'age'}, axis=1)
df20['season'] = 2020

# reformat table into long format
stars = pd.concat([df16, df17, df18, df19, df20])
#stars['season'] = pd.to_datetime(stars.season, format='%Y')

# fix misspelled player names and lowercase everything
stars['player'] = stars.player.str.strip()
stars.player.replace('Bradly Beal', 'Bradley Beal', inplace=True)
stars.player.replace('Ressell Westbrook', 'Russell Westbrook', inplace=True)
stars.player.replace('Ressell Westbrook', 'Russell Westbrook', inplace=True)
stars['player'] = stars.player.str.lower()

#%% Injury Data

miss = pd.read_csv(datadir + '/abscences.csv', index_col=0, parse_dates=['date'])

# lowercase all player names
miss['player'] = miss.player.str.lower()


team_names = {'76ers':'PHI', 'Blazers':'POR', 'Bucks':'MIL', 'Bulls':'CHI', 'Cavaliers':'CLE', 'Celtics':'BOS', 'Clippers':'LAC',  'Grizzlies':'MEM', 'Hawks':'ATL', 'Heat':'MIA', 'Hornets':'CHO','Jazz':'UTA', 'Kings':'SAC', 'Knicks':'NYK', 'Lakers':'LAL', 'Magic':'ORL', 'Mavericks':'DAL', 'Nets':'BRK','Nuggets':'DEN', 'Pacers':'IND', 'Pelicans':'NOP', 'Pistons':'DET', 'Raptors':'TOR', 'Rockets':'HOU', 'Spurs':'SAS', 'Suns':'PHO', 'Thunder':'OKC', 'Timberwolves':'MIN', 'Warriors':'GSW', 'Wizards':'WAS'}

# remove rows where team is NaN or 'Bullets'
miss = miss[pd.notnull(miss.team)]
miss = miss[miss.team != 'Bullets'] 

# replace team name with abbreviation to match other tables
miss['team'] = miss.team.replace(team_names)

# add a season column according date of the action
# regular_season date dictionary: {'season year': ['startdate','endate']}
reg_dates = {'2016': [pd.to_datetime('2015-10-27'), pd.to_datetime('2016-04-13')],
             '2017':[pd.to_datetime('2016-10-25'),pd.to_datetime('2017-04-12')],
             '2018':[pd.to_datetime('2017-10-17'),pd.to_datetime('2018-04-11')],
             '2019':[pd.to_datetime('2018-10-16'),pd.to_datetime('2019-04-13')],
             '2020':[pd.to_datetime('2019-10-22')]}

# new season starts on beginning of the regular season
miss['season'] = np.where(miss.date < reg_dates['2020'][0], 2019, 2020)
miss['season'] = np.where(miss.date < reg_dates['2019'][0], 2018, miss['season'])
miss['season'] = np.where(miss.date < reg_dates['2018'][0], 2017, miss['season'])
miss['season'] = np.where(miss.date < reg_dates['2017'][0], 2016, miss['season'])

#%% Make rest labels



def get_data(player_name):
    """Given a player name, output a combined table of player and table data 
    including fields for injury/suspension and rest labels"""
    
    player_name = player_name.lower()
        
    # subset injury data to that of the player
    df_miss = miss.query('player == @player_name')
    
    # get combination of team and the season year for the player
    player_seasons = df_miss.groupby(['season', 'team']).size().index.to_list()
    
    # get list of dates games that player played according to the team they played with that season    
    df_bask = bask.set_index(['season','team']).loc[player_seasons].reset_index()
    game_dates = df_bask.date.to_list()
    
    # acquired dates
    doA = df_miss.query('action == "acquired"')['date']
    # relinquished dates
    doR = df_miss.query('action == "relinquished"')['date']

    # find the dates that the player rested and did not play
    rest_dates = df_miss[(df_miss.notes.str.contains('rest ')) & (df_miss.action == 'relinquished')]['date'].to_list()
    rest_array = np.isin(game_dates, rest_dates).astype(int)
    
    reg_dates = {'2016': [pd.to_datetime('2015-10-27'), pd.to_datetime('2016-04-13')],
             '2017':[pd.to_datetime('2016-10-25'),pd.to_datetime('2017-04-12')],
             '2018':[pd.to_datetime('2017-10-17'),pd.to_datetime('2018-04-11')],
             '2019':[pd.to_datetime('2018-10-16'),pd.to_datetime('2019-04-13')],
             '2020':[pd.to_datetime('2019-10-22')]}

    df_temp = pd.DataFrame(pd.date_range(reg_dates['2016'][0], reg_dates['2020'][0], freq='D')).rename({0:'time'}, axis=1)
    df_temp['doG'] = np.isin(df_temp.time, game_dates)
    df_temp['doA'] = np.isin(df_temp.time, doA).astype(int)
    df_temp['doR'] = np.isin(df_temp.time, doR).astype(int)
    season_dates = pd.Series([item for sublist in list(reg_dates.values()) for item in sublist])
    df_temp['season'] = np.isin(df_temp.time, season_dates)
    df_temp['rest'] = np.isin(df_temp.time, pd.Series(rest_dates)).astype(int) 
    df_temp['absent'] = pd.Series(df_temp.doA + df_temp.season + df_temp['rest'] - df_temp.doR).replace({0, np.NaN})
    df_temp['absent'] = df_temp['absent'].ffill().replace({1:0, -1:1})
    
#    df = df_temp[df_temp['doG']]
    
    df_bask['player'] = player_name
    df_bask['absent'] = df_temp['absent']
    df_bask['rest'] = rest_array
    df_bask['rest'] = df_miss
    
    return df_bask


#%%
    

lebron = get_data('lebron james')
#lebron.to_csv('lebron.csv')

lebron.head()

print("Lebron rest days: %d" %lebron.rest.sum())
print("Lebron injured days: %d" %lebron.absent.sum())
