dat = read.csv("df_all.csv")
dat$rest = as.factor(dat$rest)
dat = subset(dat, dat$season== "2016" | dat$season == "2017" | dat$season == "2018")

dat$season = as.factor(dat$season)


for(i in 1:length(dat$days_rest)){
  if(abs(dat$days_rest[i])>20){
    dat$days_rest[i] = 8
  }
}

dat$win_prob = 0

for(i in 1:length(dat$days_rest)){
  if(dat$team1..Home.[i] == dat$team[i]){
    dat$win_prob[i] = dat$elo_prob1[i]}
  else{
    dat$win_prob[i] = dat$elo_prob2[i]}
}

dat$home = as.factor(dat$home)
dat$rest = as.factor(dat$rest)
dat$b2b = as.factor(dat$b2b)

dat$df2.playoff_prob = abs(dat$df2.playoff_prob - 0.5)

mod1 = glm(rest~season + b2b + days_rest + df2.playoff_prob + miles + home + win_prob + born, family = "binomial", data = dat)

summary(mod1)

library(MASS)
stepAIC(mod1, direction = "both")

mod2 = glm(rest~season + days_rest + home + df2.playoff_prob + born, family = "binomial", data = dat)
summary(mod2)

library(dplyr)

dums = data.frame(predict(mod1, dat, type="response"))
dums2 = data.frame(predict(mod2, dat, type="response"))


dat2 = subset(dat, dat$rest == 0)
dat3 = subset(dat, dat$rest == 1)
dat4 = dat2[sample(nrow(dat2), 561, replace = FALSE), ]
dat5 = rbind(dat4, dat3)

mod3 = glm(rest~season + b2b + days_rest + df2.playoff_prob + miles + home + win_prob + born, family = "binomial", data = dat5)

library(MASS)
stepAIC(mod3, direction = "both")

mod4 = glm(rest~season + days_rest + home + df2.playoff_prob + born, family = "binomial", data = dat5)
summary(mod4)
dums3 = data.frame(predict(mod4, dat5, type="response"))
dums7 = as.factor(ifelse(dums3>0.5,1,0))

library(caret)
confusionMatrix(dums7, dat5$rest)

dums3b = data.frame(predict(mod4, dat, type="response"))
dums7b = as.factor(ifelse(dums3b>0.5,1,0))

library(caret)
confusionMatrix(dums7b, dat$rest)


#----------------------------------------------------------------------------------------



df_big = read.csv("df_all2.csv")
library(anytime)
df_big$date  = anydate(df_big$date)

df_big$b2b = 0
for(i in 2:length(df_big$date)){
  if(df_big$date[i] - df_big$date[i-1] == 1){
    df_big$b2b[i] = 1
    df_big$b2b[i-1] = 1
  }
}

df_big$df2.playoff_prob = abs(df_big$df2.playoff_prob - 50)

df_big$missed_last = 0
for(i in 2:length(df_big$date)){
  if(df_big$rest[i-1] == 1){
    df_big$missed_last[i] = 1
  }
}

df_big$season = as.factor(df_big$season)
df_big$home = as.factor(df_big$home)
df_big$rest = as.factor(df_big$rest)
df_big$b2b = as.factor(df_big$b2b)
df_big$missed_last = as.factor(df_big$missed_last)

mod_big = glm(rest~season+ game + days_rest + home + df2.playoff_prob+ oppo_playoff_prob + age + b2b + missed_last + miles, family = "binomial", data = df_big)

stepAIC(mod_big, direction = "both")

mod_big2 = glm(rest~season+ game + days_rest + home + df2.playoff_prob+ age + b2b + missed_last, family = "binomial", data = df_big)
summary(mod_big2)
dums4 = data.frame(predict(mod_big2, df_big, type="response"))

indexes <- sample(1:nrow(df_big), size = 0.75*nrow(df_big))

train <- df_big[indexes,]
test <- df_big[-indexes,]

mod_big2_train = glm(rest~season+ game + days_rest + home + df2.playoff_prob+ age + b2b + missed_last, family = "binomial", data = train)
summary(mod_big2)
dums5 = data.frame(predict(mod_big2_train, test, type="response"))
dums6 = as.factor(ifelse(dums5>0.5,1,0))

library(caret)
confusionMatrix(dums6, test$rest)
summary(test)
