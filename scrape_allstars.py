#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Nick Clifford
# NBA Rest Proj

# =============================================================================
# This script creates the allstar.csv data file, which contains the names, team, 
# and year of every NBA All-Star player from some specified year to the present.
# This is done by crawling the basketball-reference.com website. 
# =============================================================================

#%% Setup

import requests
import pandas as pd
import itertools
from bs4 import BeautifulSoup

# allstar seasons to consider, 2015 is the 2014-2015 season
seasons = list(range(2016, 2021))
# path to the data directory
datadir = 'data/'

def combine(List):
    """Input a list that contains multiple sublists within and join all sublists into one"""
    return list(itertools.chain.from_iterable(List))

#%% Scrape All-Star Webpages for Player Data

# base url path to basketball-references list of allstar games
rooturl = 'https://www.basketball-reference.com/allstar/NBA_'

# initialize lists to hold the data for each column
allstar_players, allstar_teams, allstar_season = [], [], []

# look through each allstar year url
for year in seasons:
    # pull html text from the allstar webpage
    response = requests.get(rooturl + str(year) + '.html')
    soup = BeautifulSoup(response.text, 'lxml')
    
    # get list names of allstars
    players_html = soup.find_all('th', {'scope':'row'})
    players_list = [player.text for player in players_html if player.text != 'Team Totals'] # extract text from the html elements
    # get list of teams of allstar players
    teams_html = soup.find_all('td', {'class':'left'})
    teams_list = [team.text for team in teams_html if team.text != ''] # extract text from the html elements
    # create same sized list of the allstar season year
    season_list = [year]*len(teams_list)
    
    # combine data from each season into single lists
    allstar_players.append(players_list)
    allstar_teams.append(teams_list)
    allstar_season.append(season_list)

# combine each list of lists and put them in dict where 'key' is the col name
allstar_dict = {'player':combine(allstar_players), 'team':combine(allstar_teams), 'season':combine(allstar_season)}
# convert to DataFrame
allstar = pd.DataFrame.from_dict(allstar_dict)
# write DataFrame to .csv file
allstar.to_csv(datadir+'allstar.csv', index=False)

