#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Nick Clifford
# NBA Rest Proj

# =============================================================================
# This script creates the absences.csv file, which contains every instance an NBA 
# player was relinquished from or added back onto the active roster from the start 
# of the 2015-16 season to present, along with a description for why the player
# was removed. This is done by scraping the Pro Sports Transactions website. 
# =============================================================================

#%% Setup

import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

# path to the data directory
datadir = 'data/'


#%% Get list of URLs to crawl

# Pro Sports Transaction and search player missed games from 2015 to present
url = 'http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2015-10-27&EndDate=&ILChkBx=yes&InjuriesChkBx=yes&PersonalChkBx=yes&DisciplinaryChkBx=yes&Submit=Search'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# last table contains hyperlinks for rest of search result pages
link_table = soup.find_all('table')[-1]

link_list = []
for a in link_table.find_all('a',href=True):
        link_list.append(a['href'])

print('Number of page links: %d' %(len(link_list)))

#%% Scrape Absence Table

# Initialize dict where key:list pair is a column of the dataset
table_dict = {'date':[], 'team':[], 'player':[], 'action':[], 'notes':[]}

# crawl through every results page
for link in tqdm(link_list, unit='page', position=0, leave=True):
    # retrieve html text from url
    response = requests.get('http://www.prosportstransactions.com/basketball/Search/' + link)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # last table contains hyperlinks for rest of search result pages
    data_table = soup.find_all('table')[0]
    
    # first row contains column headers
    rows = data_table.find_all('tr')[1:]
    
    # retrieve data from each html table
    for row in rows:
        # text of row field contained in td tags
        row_list = row.find_all('td')
        
        date = row_list[0].text
        team = row_list[1].text.strip()
        # melt relinquished/acquired fields into one action col, key col being the player name
        if len(row_list[2].text) == 1:
            action = 'relinquished'
            player = row_list[3].text.strip(' •')
        elif len(row_list[3].text) == 1:
            action = 'acquired'
            player = row_list[2].text.strip(' •')
        notes = row_list[4].text.lstrip()
        
        # add text into their respective fields
        table_dict['date'].append(date)
        table_dict['team'].append(team)
        table_dict['player'].append(player)
        table_dict['action'].append(action)
        table_dict['notes'].append(notes)

# convert dict to DataFrame 
df = pd.DataFrame.from_dict(table_dict)
# write DataFrame to .csv file
df.to_csv(datadir+'abscences.csv')