#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:24:18 2020

@author: Nick Clifford
"""

#%% Import modules

import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
#%% Get list of urls to crawl

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

#%% Get Table


table_dict = {'date':[], 'team':[], 'player':[], 'action':[], 'notes':[]}

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

df = pd.DataFrame.from_dict(table_dict)
df.to_csv('data/abscences.csv')


#%% Look at data

df.date = pd.to_datetime(df.date)

df.query('player == "LeBron James"')
