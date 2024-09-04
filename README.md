# Predicting when NBA Stars will rest

*This was orginially a group class project that I've been interested in continuing. I'm only including work that is my own, and am currently in the process of rewriting all code that is not mine. This is still a work in progress.*

![alt text](https://i.insider.com/5dc5e1623afd3701a027c603?width=1260&format=jpeg&auto=webp)
## Problem
Inactivity among NBA players has been on the rise in the past 5 years. While injury risk has remained relatively constant, the recent seasons have seen an uptick in star players electing not to take the court during regular-season games to mitigate the risks of injury and fatigue during the playoffs. Modeling the likelihood that a player takes the court for a given game can be advantageous for opposing teams who can develop gameplans around the lineup they’re most likely to face as opposed to the best lineup their opponents can assemble. It also has applications in sports betting and fan experience, where fantasy lineups are set with this information in mind, and insurance policies are being offered to those who purchased tickets in the event a given player does not take the court. The goal is to utilize neural networks to build a model that predicts whether a given player will sit out for a particular game. Currently, similar existing models rely on logistic regression but could be developed using any machine learning solution aimed at binary classification, including neural networks.

## Research
- [Load management is the NBA’s hottest term. What does it mean?](https://www.sbnation.com/nba/2019/11/8/20954096/load-management-definition-kawhi-leonard-lebron-james-fines-controversy) (Matt Ellentuck, SBNation (2019))

This article details the creation of the DNP-rest tactic started by the San Antonio Spurs in 2012 and the backlash received from the league and its fans, but, more importantly, describes how and when it is utilized. With the league’s grueling 82 game schedule combined with constant traveling and time-zone changes, **teams with good positions to make the playoffs are more inclined to bench their top players in hopes of improving future playoff game chances.** Factors like nationally broadcasted games may take affect if stars are less likely to be benched, but star players still occasionally rest these games nonetheless. Compromises of improving the league’s schedule are nowhere in sight and the loosening grip of league fines means coaches will be more likely to bench their stars while fans are at greater risk of missing out on watching their favorite athletes play. 

- [Game injuries in relation to game schedules in the National Basketball Association](https://www-sciencedirect-com.proxy01.its.virginia.edu/science/article/pii/S1440244016301633) (Teramoto et al (2017))

This study set out to examine the association between NBA players’ game schedules and their injuries experienced during the 2012-13 & 2014-15 regular seasons. A Poisson regression analysis was used to predict the number of injuries sustained by each player based on game schedules and the players’ profiles. They found that playing **back-to-back away games were significant predictors of frequent game injuries (p < 0.05)** and the **odds of such injuries were 3.5 times higher than the odds of those occurring in home games.** Working under the assumption that team coaches are aware of the added injury risk from back-to-back away games, I felt that incorporating this information into the model design is critical. 

## Data
### Collection
The following project utilizes player & team-level NBA data from the past 5 years (2016-20). Due to the difficulty of finding a premade dataset that captures the key features for this project, the data must be collected from various sources and combined manually. 

- On the player-level, I am only interested in players whom the topic at hand actually relates to. Therefore, I will subset all player data to those selected as All-Stars for the following seasons in question. For this, I turned to [basketball-reference.com](https://www.basketball-reference.com/)
- [FiveThirtyEight](https://data.fivethirtyeight.com/) keeps a record of each NBA game, of which, we are interested in things like: teams played, date, and the pregame win probabilities of each team. [FiveThirtyEight](https://data.fivethirtyeight.com/) also publicly inlcudes the weekly probabilities that each team will make teh playoffs in their current season! 
- Based on the findings of Teramoto et al (2017), we should also inlcude association between each team's travel distance before games. This [script from github user myzeiri](https://github.com/myzeiri/Distances-Between-Cities) queries WolframAlpha to return distances between cities, which I'll use to create a 30x30 distance matrix. 
- Probably the most difficult task involves collecting the actual target variable: whether or not a player sat out for their game. [Pro Sports Transactions](http://www.prosportstransactions.com/basketball/Search/Search.php) contains nearly all information on player inactivity across many sports, which I use to [scrape NBA player absences](scrape_absences.py)

**It should also be noted that NBA rules allowed players to miss a game for "rest" up until the 2018 season. Afterwards, players must have an official injury designation making it difficult to extract our player rest target variable. For the time being, I've decided to split the question into 2 parts:**
1. **Can we predict when a player is going to rest a game from seasons 2016-18?**
2. **Can we predict when a player is simply inactive (rest, injury, ejection, etc) from seasons 2016-20?**

After I gather all pieces of the data (team, all-stars, inactivity/rest-labels), I [clean it up and combine them](make_data.py) into 2 datasets. Binary target variables for both are either 1 for a rested player or 1 (2016-18) for inactive (2016-20). 

### Feature Engineering
Once gathered, we can add some key features which might improve model performance. 

- Number of days in-between games using date of games
- Whether a set of games were part of a back-to-back schedule (binary)
- Whether the team was home or away (binary)
- Team of interest's playoff probability as of the date of the game 


## Methods
Since the likelihood that a given player participates in a particular game is time-dependent, we shall develop a predictive model using recurrent neural network architecture. We want to compare the accuracy of this model to one using logistic regression. Inputs to the model will include features of the player and team immediately before the game as well as the value of said features before previous games. This being a classification problem the final layer will have a sigmoidal activation function and the model will look to minimize binary cross-entropy

