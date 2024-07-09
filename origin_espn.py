import os
import pandas as pd
import pyodbc 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import datetime
from datetime import timedelta
from dateutil.parser import parse
from selenium.webdriver.common.by import By
import pytz
import time
from webdriver_manager.chrome import ChromeDriverManager
import ssl
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

server = 'sql5030.smarterasp.net'
database = 'DB_A17D64_trinovitech'
username = 'DB_A17D64_trinovitech_admin'
password = 'Schmuck@dmin1!'
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password + ';Trusted_Connection=no')
cursor = cnxn.cursor()
# ssl._create_default_https_context = ssl._create_unverified_context

seasonType = '1'
year = "2023"
week = "4"
isPast = False

scoreDetails = []
parent_div_all = []
# url = 'https://www.espn.com/nfl/scoreboard/_/year/' + year + '/seasontype/' + seasonType + '/week/' + week
url = 'https://www.espn.com/nfl/scoreboard/_/week/' + week + '/year/' + year + '/seasontype/' + seasonType
print('******************************** Start *****************************')

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ['enable-logging'])
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get(url)

def solve(day):
  if 4 <= day <= 20 or 24 <= day <= 30:
      suffix = "th"
  else:
      suffix = ["st", "nd", "rd"][day % 10 - 1]
  return str(day) + suffix    

def checkInt(str):
    try:
        int(str)
        return True
    except ValueError:
        return False
# Insert Board
print('=============================== Board ===============================')

#articles = driver.find_elements_by_css_selector("div#events > article")
articles= driver.find_elements(By.XPATH, "//section[@class='Scoreboard bg-clr-white flex flex-auto justify-between']")

article_index = 0
aux_date_time_str = ""
for article in articles:
  article_index += 1
  container_id = article.get_attribute('id')
  home_team = article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--home .ScoreCell__TeamName").text.strip()
  # for team in Teams:
  #   home_team=team.text.strip()
  away_team = article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--away .ScoreCell__TeamName").text.strip()
  print(away_team, home_team)
  home_score = ""
  away_score = ""
  season = ""
  str_matchup_date = ""
  UtcTime=""
  game_time=""
  
  if article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Time"):
    season = article.find_element(By.CSS_SELECTOR, " .ScoreboardScoreCell__Time").text.strip()
    print("season : " +season)
  if article.find_elements(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--home .ScoreCell__Score"):
    home_score = article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--home .ScoreCell__Score").text.strip()
    print("home_score : "+home_score)
  if article.find_elements(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--away .ScoreCell__Score"):
    away_score = article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--away .ScoreCell__Score").text.strip()
    print("away_score : "+away_score)
  parent_div_c = article.find_elements(By.XPATH, "//section[@class='Card gameModules']")
  
  for p_div in parent_div_c:
    parent_div = p_div.get_attribute('innerHTML')
    parent_div_all.append(parent_div)
    
  matching = [s for s in parent_div_all if home_team in s]
  index_val = parent_div_all.index(matching[0])
  parent_divv = driver.find_elements(By.XPATH, "//section[@class='Card gameModules']")
  if parent_div_c[index_val].find_element(By.CSS_SELECTOR, ".Card__Header__Title__Wrapper h3") != None:
    date_time_st = parent_div_c[index_val].find_element(By.CSS_SELECTOR, ".Card__Header__Title__Wrapper h3").text.strip()
    aux_date_time_str = date_time_st
    print(date_time_st)
    arr = date_time_st.split(',')   
    date_time_str =arr[1].lstrip()+","+arr[2]
    date_time = datetime.datetime.strptime(date_time_str, '%B %d, %Y').strftime('%Y-%m-%d %H:%M:%S')
    date_format_str = '%Y-%m-%d %H:%M:%S'
    given_time = datetime.datetime.strptime(date_time, date_format_str)
    #date_time1 = parse(date_time_str + " " + year)
    date = str(given_time).split(" ")[0]
   # date = date_time_str.split("T")[0]   # Utc date
  else:
    date_time_str = parent_div_c[0].find_element(By.CSS_SELECTOR, ".Card__Header__Title__Wrapper h3").text.strip()
    aux_date_time_str = date_time_str
    arr = date_time_st.split(',')
    date_time_str =arr[1].lstrip()+","+arr[2]
    date_time = datetime.datetime.strptime(date_time_str, '%B %d, %Y').strftime('%Y-%m-%d %H:%M:%S')
    date_format_str = '%Y-%m-%d %H:%M:%S'
    given_time = datetime.datetime.strptime(date_time, date_format_str)
    date = str(given_time).split(" ")[0]
  matchUpKey = date + away_team + home_team

  home_abbrev = article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--home a").get_attribute('href')
  away_abbrev = article.find_element(By.CSS_SELECTOR, ".ScoreboardScoreCell__Item--away a").get_attribute('href')
  isLine = 1
  away_spread = ""
  home_spread = ""
  total_over = ""
  total_under =""
  spread = ""  
  game_time = season
  print("game_time is: ", game_time, " date from given_time is: ", date)
  try:
    odds_message = article.find_element(By.CSS_SELECTOR, "div.Scoreboard__Column--2 .Odds__Message").text.split('\n')
    try:
      line = odds_message[0].split(":")[1].strip()
      o_u = odds_message[1].split(":")[1].strip()
    except IndexError:
      o_u = "" 
    if odds_message[0].split(":")[0].strip() == "Line" and odds_message[0].split(":")[0].strip() != "EVEN"and odds_message[0].split(":")[1].strip() != "EVEN":
      favTeam = line.split(" ")[0].lower()
      spread = line.split(" ")[1]
      if(favTeam in str(home_abbrev)):
        home_spread = spread
      if(favTeam in str(away_abbrev)):
        away_spread = spread
    total_over = total_under = o_u
  except NoSuchElementException:
    # home_spread = ""
    # away_spread = ""
    # total_over = ""
    # total_under = ""
    isLine = 0

  scoreUrls = article.find_elements(By.CSS_SELECTOR ,".Scoreboard__Callouts>a")
  if("FINAL" in season and isPast == False):
    # Running if inserting games into Board in the future because there is a game time
    GameTime = date + " " + "00:00"
    utcGameTime = "FINAL"
  elif("FINAL" in season and isPast == True): 
    GameTime = date + " " + "00:00"
    format  = "%Y-%m-%d %H:%M"
    localGameTime = datetime.datetime.strptime(GameTime, format)
    utcGameTime = localGameTime.astimezone(pytz.UTC)
    dtGameTime = utcGameTime.strftime(format)
  elif("Halftime" in season):
    GameTime = date + " " + "00:00"
    utcGameTime = "HALF"
  elif("CANCELED" in season):
    utcGameTime = "CANCELED"
  else:
    if(len(season.split(" ")) == 3):
      if(checkInt(season.split(" ")[0].split(":")[0])):
        if(int(season.split(" ")[0].split(":")[0]) < 13):
          season = season.split(" ")[0] + " AM"
        else:
          season = str(int(season.split(" ")[0].split(":")[0]) - 12)  + ":" + season.split(" ")[0].split(":")[1] + " PM"
      else:
        season = "00:00 AM"
    # if(len(season.split(":")[0]) == 1):
    #   season = "0" + season
    stripTime = datetime.datetime.strptime(season, '%I:%M %p')
    game24hrTime = stripTime.strftime("%H:%M")
    GameTime = date + " " + game24hrTime
    format  = "%Y-%m-%d %H:%M"
    localGameTime = datetime.datetime.strptime(GameTime, format)
    utcGameTime = localGameTime.astimezone(pytz.UTC)
    dtGameTime = utcGameTime.strftime(format)
    
  # CHECK YOUR TIMES
    print("GAME TIMES: ", localGameTime, utcGameTime, dtGameTime)
    
  for score_text in scoreUrls:
    if score_text.text == 'BOX SCORE':
      scoreUrl = score_text.get_attribute('href')
    else:
      scoreUrl=""
    scoreDetails.append({"url" : scoreUrl, "fkMatchupKey" : matchUpKey, "MatchupDate" : date_time_str})

  SqlSelectCommand = ("SELECT * FROM dbo.Board WHERE MatchupKey=?")
  Values = [matchUpKey]
  row = cursor.execute(SqlSelectCommand, Values)
  if(len(row.fetchall()) == 0):

    SQLInsertCommand = ("INSERT INTO dbo.Board (MatchupKey, fkSportKey, Date, AwayTeam, HomeTeam, SpreadAway, SpreadHome, TotalUnder, TotalOver, ScoreAwayTotal, ScoreHomeTotal, Season, GameTime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)")
    Values = [matchUpKey, 1, dtGameTime, away_team, home_team, away_spread, home_spread, total_under, total_over, away_score, home_score, season, game_time]
    cursor.execute(SQLInsertCommand,Values)
  else:
    if(isLine == 0 ):
      Values = [away_team, home_team, away_score, home_score, utcGameTime, game_time, matchUpKey]
      SQLUpdateCommand = ("UPDATE dbo.Board SET AwayTeam=?, HomeTeam=?, ScoreAwayTotal=?, ScoreHomeTotal=?, Season=?, GameTime=? WHERE MatchupKey=?")
      cursor.execute(SQLUpdateCommand, Values)
    else:
        Values = [away_team, home_team, away_spread, home_spread, total_under, total_over, away_score, home_score, utcGameTime, game_time, matchUpKey]
        SQLUpdateCommand = ("UPDATE dbo.Board SET AwayTeam=?, HomeTeam=?, SpreadAway=?, SpreadHome=?, TotalUnder=?, TotalOver=?, ScoreAwayTotal=?, ScoreHomeTotal=?, Season=?, GameTime=? WHERE MatchupKey=?")
        cursor.execute(SQLUpdateCommand, Values)
  #contest winner
  try:
    SqlSelectCommand = ("SELECT * FROM dbo.ContestIterations WHERE fkMatchupKey=?")
    Values = [matchUpKey]
    row = cursor.execute(SqlSelectCommand, Values)
    contests = row.fetchall()
    if(len(contests) != 0):
      for contest in contests:
        MatchupKey=contest.fkMatchupKey
        ContestIterationsKey=contest.ContestIterationsKey
        
        SqlSelectCommand = ("SELECT * FROM dbo.Board WHERE MatchupKey=? AND Season LIKE ? AND MatchupKey NOT IN (SELECT fkMatchupKey FROM ContestWinners WHERE fkMatchupKey = ? AND fkContestIterationsKey = ?)")
        Values = [MatchupKey, "%FINAL%", MatchupKey, ContestIterationsKey]
        row= cursor.execute(SqlSelectCommand, Values)
        final_rows = row.fetchall()
        if (len(final_rows) != 0):
            print("homeTeam: ",final_rows[0].HomeTeam," awayTeam: ", final_rows[0].AwayTeam)
            if (final_rows[0].ScoreHomeTotal > final_rows[0].ScoreAwayTotal):
              winner_score = final_rows[0].ScoreHomeTotal
              winner_team = final_rows[0].HomeTeam
            else:
              winner_score = final_rows[0].ScoreAwayTotal
              winner_team = final_rows[0].AwayTeam
              
            #insert winner
            SQLInsertCommand = ("INSERT INTO dbo.ContestWinners (fkContestIterationsKey, Winner, BonusPickWinner, fkMatchupKey) VALUES (?,?,?,?)")
            Values = [ContestIterationsKey, winner_team, winner_score, MatchupKey]
            cursor.execute(SQLInsertCommand,Values)     
        # else:
        #     #update winner
        #     Values = [ContestIterationsKey, winner_team, winner_score, MatchupKey]
        #     SQLUpdateCommand = ("UPDATE dbo.ContestWinners SET fkContestIterationsKey=?, Winner=?, BonusPickWinner=? WHERE fkMatchupKey=?")
        #     cursor.execute(SQLUpdateCommand,Values)  
    cnxn.commit()
  
    print("MatchUpKey=" + matchUpKey,", Date=" + str(date_time))
  except NoSuchElementException:
      print("error") 

if(len(scoreDetails) > 0):

  print('============================= Box Score =============================')
  for scoreDetail in scoreDetails:
    if scoreDetail["url"] != "": 
    # IGNORE FINAL GAMES TO INCREASE EFFICIENCY
      # fkMatchupKey = scoreDetail["fkMatchupKey"]
      # SqlSelectCommand = ("SELECT * FROM dbo.Board WHERE MatchupKey=? AND Season NOT LIKE ?")
      # Values = [fkMatchupKey, "%FINAL%"]
      # row= cursor.execute(SqlSelectCommand, Values)
      # game_start = row.fetchall()
      # if (len(game_start) != 0):
      #   for game in game_start:
      #     if (game.Date + timedelta(hours=4) > datetime.datetime.now()):
      #       MatchupDate = scoreDetail["MatchupDate"]       
      #       driver.get(scoreDetail["url"])
      
    # USE THIS FOR COMPLETE STATS, FOR CONSTITUTING THE STATS FOR EXAMPLE
      driver.get(scoreDetail["url"])
      fkMatchupKey = scoreDetail["fkMatchupKey"]
      MatchupDate = scoreDetail["MatchupDate"]
      gameRows = driver.find_elements(By.CSS_SELECTOR ,".Boxscore__Category")
      for gameRow in gameRows:
        gameType = gameRow.find_element(By.CSS_SELECTOR, "div.TeamTitle > div").text.strip()
        if "Passing" in gameType:
          print("--------------------------- Passing ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              CompAttempt = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              PassingYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              PassingTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              PassingINT = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              PassingSacks = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(6)").text.strip()
              try:
                PassingQBR = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(7)").text.strip()
              except NoSuchElementException:
                PassingQBR = ""
              print("Passing::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, CompAttempt, PassingYds, PassingTD, PassingINT, PassingSacks, PassingQBR)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGamePassing WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGamePassing (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, CompAttempt, PassingYds, PassingTD, PassingINT, PassingSacks, PassingQBR) VALUES (?,?,?,?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, CompAttempt, PassingYds, PassingTD, PassingINT, PassingSacks, PassingQBR]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [CompAttempt, PlayerTeam, PassingYds, PassingTD, PassingINT, PassingSacks, PassingQBR, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGamePassing SET CompAttempt=?, PlayerTeam=?, PassingYds=?, PassingTD=?, PassingINT=?, PassingSacks=?, PassingQBR=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()          
        if "Rushing" in gameType:
          print("--------------------------- Rushing ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              Carries = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              RushYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              RushTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              RushLong = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              print("Rushing::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, Carries, RushYds, RushTD, RushLong)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameRushing WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameRushing (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, Carries, RushYds, RushTD, RushLong) VALUES (?,?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, Carries, RushYds, RushTD, RushLong]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [Carries, PlayerTeam, RushYds, RushTD, RushLong, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameRushing SET Carries=?, PlayerTeam=?, RushYds=?, RushTD=?, RushLong=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()        
        if "Receiving" in gameType:
          print("--------------------------- Receiving ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              Receptions = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              ReceivingYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              ReceivingTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              ReceivingLong = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              ReceivingTgts = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(6)").text.strip()
              print("Receiving::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, Receptions, ReceivingYds, ReceivingTD, ReceivingLong, ReceivingTgts)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameReceiving WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0 and len(PlayerName) > 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameReceiving (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, Receptions, ReceivingYds, ReceivingTD, ReceivingLong, ReceivingTgts) VALUES (?,?,?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, Receptions, ReceivingYds, ReceivingTD, ReceivingLong, ReceivingTgts]
                cursor.execute(SQLInsertCommand, Values)
              elif(len(PlayerName) > 0):
                Values = [PlayerTeam, Receptions, ReceivingYds, ReceivingTD, ReceivingLong, ReceivingTgts, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameReceiving SET PlayerTeam=?, Receptions=?, ReceivingYds=?, ReceivingTD=?, ReceivingLong=?, ReceivingTgts=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()
        if "Fumbles" in gameType:
          print("--------------------------- Fumbles ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              Fumbles = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              FumblesLost = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              FumblesRecovered = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(3)").text.strip()
              print("Fumbles::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, Fumbles, FumblesLost, FumblesRecovered)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameFumbles WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameFumbles (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, Fumbles, FumblesLost, FumblesRecovered) VALUES (?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, Fumbles, FumblesLost, FumblesRecovered]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, Fumbles, FumblesLost, FumblesRecovered, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameFumbles SET PlayerTeam=?, Fumbles=?, FumblesLost=?, FumblesRecovered=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()
        if "Defensive" in gameType:
          print("--------------------------- Defensive ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              # PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,".Boxscore__Athlete_Name").text.strip()
              TotalTackles = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              SoloTackles = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              DefSacks = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(3)").text.strip()
              TacklesForLoss = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              PassesDefensed = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              QBHits = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(6)").text.strip()
              DefTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(7)").text.strip()
              # PassesDefensed = ""
              # QBHits = ""
              # DefTD = ""
              print("Defensive::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, TotalTackles, SoloTackles, DefSacks, TacklesForLoss, PassesDefensed, QBHits, DefTD)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameDefensive WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameDefensive (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, TotalTackles, SoloTackles, DefSacks, TacklesForLoss, PassesDefensed, QBHits, DefTD) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, TotalTackles, SoloTackles, DefSacks, TacklesForLoss, PassesDefensed, QBHits, DefTD]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, TotalTackles, SoloTackles, DefSacks, TacklesForLoss, PassesDefensed, QBHits, DefTD, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameDefensive SET PlayerTeam=?, TotalTackles=?, SoloTackles=?, DefSacks=?, TacklesForLoss=?, PassesDefensed=?, QBHits=?, DefTD=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()          
        if "Interceptions" in gameType:
          print("--------------------------- Interceptions ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              GameINTs = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              GameINTYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              GameINTTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(3)").text.strip()
              print("Interceptions::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, GameINTs, GameINTYds, GameINTTD)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameINT WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameINT (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, GameINTs, GameINTYds, GameINTTD) VALUES (?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, GameINTs, GameINTYds, GameINTTD]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, GameINTs, GameINTYds, GameINTTD, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameINT SET PlayerTeam=?, GameINTs=?, GameINTYds=?, GameINTTD=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()         
        if "Punt Returns" in gameType:
          print("--------------------------- Punt Returns ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              ReturnNum = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              ReturnYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              ReturnAvg = ""
              ReturnLong = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              ReturnTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              print("Punt Returns::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameKickPuntReturns WHERE fkMatchupKey=? and PlayerName=? and ReturnType='Punt'")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameKickPuntReturns (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD, ReturnType) VALUES (?,?,?,?,?,?,?,?,?,'Punt')")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameKickPuntReturns SET PlayerTeam=?, ReturnNum=?, ReturnYds=?, ReturnAvg=?, ReturnLong=?, ReturnTD=?, ReturnType='Punt' WHERE fkMatchupKey=? and PlayerName=? and ReturnType='Punt'")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()          
        if "Kick Returns" in gameType:
          print("--------------------------- Kick Returns ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              ReturnNum = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              ReturnYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              ReturnAvg = ""
              ReturnLong = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              ReturnTD = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              print("Kick Returns::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameKickPuntReturns WHERE fkMatchupKey=? and PlayerName=? and ReturnType='Kick'")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameKickPuntReturns (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD, ReturnType) VALUES (?,?,?,?,?,?,?,?,?,'Kick')")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, ReturnNum, ReturnYds, ReturnAvg, ReturnLong, ReturnTD, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameKickPuntReturns SET PlayerTeam=?, ReturnNum=?, ReturnYds=?, ReturnAvg=?, ReturnLong=?, ReturnTD=?, ReturnType='Kick' WHERE fkMatchupKey=? and PlayerName=? and ReturnType='Kick'")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()          
        if "Kicking" in gameType:
          print("--------------------------- Kicking ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              PlayerFG = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              PlayerFGPct = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              PlayerFGLong = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(3)").text.strip()
              PlayerXP = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              PlayerKickingPts = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              print("Kicking::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, PlayerFG, PlayerFGPct, PlayerFGLong, PlayerXP, PlayerKickingPts)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGameKicking WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGameKicking (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, PlayerFG, PlayerFGPct, PlayerFGLong, PlayerXP, PlayerKickingPts) VALUES (?,?,?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, PlayerFG, PlayerFGPct, PlayerFGLong, PlayerXP, PlayerKickingPts]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, PlayerFG, PlayerFGPct, PlayerFGLong, PlayerXP, PlayerKickingPts, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGameKicking SET PlayerTeam=?, PlayerFG=?, PlayerFGPct=?, PlayerFGLong=?, PlayerXP=?, PlayerKickingPts=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()            
        if "Punting" in gameType:
          print("--------------------------- Punting ---------------------------")
          teams = gameRow.find_elements(By.CSS_SELECTOR, ".Boxscore__Team")
          for team in teams:
            PlayerTeam = team.find_element(By.CSS_SELECTOR ,"div.TeamTitle > img").get_attribute("alt")
            playerRows = team.find_elements(By.CSS_SELECTOR ,".flex > table tbody .Boxscore__Athlete")
            index = 0
            for playerRow in playerRows:
              index = index + 1
              PlayerName = playerRow.find_element(By.CSS_SELECTOR ,"a").text.strip()
              PlayerPunts = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(1)").text.strip()
              PlayerPuntYds = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(2)").text.strip()
              PlayerPuntAvg = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(3)").text.strip()
              PlayerPuntTouchBack = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(4)").text.strip()
              PlayerPuntIn20 = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(5)").text.strip()
              PlayerPuntLong = team.find_element(By.CSS_SELECTOR ,".flex > div tbody tr:nth-child(" + str(index) + ") td:nth-child(6)").text.strip()
              print("Punting::", fkMatchupKey, MatchupDate, PlayerTeam, PlayerName, PlayerPunts, PlayerPuntAvg, PlayerPuntTouchBack, PlayerPuntIn20, PlayerPuntLong)
              SqlSelectCommand = ("SELECT * FROM dbo.NFLGamePunting WHERE fkMatchupKey=? and PlayerName=?")
              Values = [fkMatchupKey, PlayerName]
              row = cursor.execute(SqlSelectCommand, Values)
              if(len(row.fetchall()) == 0):
                SQLInsertCommand = ("INSERT INTO dbo.NFLGamePunting (fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, PlayerPunts, PlayerPuntYds, PlayerPuntAvg, PlayerPuntTouchBack, PlayerPuntIn20, PlayerPuntLong) VALUES (?,?,?,?,?,?,?,?,?,?)")
                Values = [fkMatchupKey, MatchupDate, PlayerName, PlayerTeam, PlayerPunts, PlayerPuntYds, PlayerPuntAvg, PlayerPuntTouchBack, PlayerPuntIn20, PlayerPuntLong]
                cursor.execute(SQLInsertCommand, Values)
              else:
                Values = [PlayerTeam, PlayerPunts, PlayerPuntYds, PlayerPuntAvg, PlayerPuntTouchBack, PlayerPuntIn20, PlayerPuntLong, fkMatchupKey, PlayerName]
                SQLUpdateCommand = ("UPDATE dbo.NFLGamePunting SET PlayerTeam=?, PlayerPunts=?, PlayerPuntYds=?, PlayerPuntAvg=?, PlayerPuntTouchBack=?, PlayerPuntIn20=?, PlayerPuntLong=? WHERE fkMatchupKey=? and PlayerName=?")
                cursor.execute(SQLUpdateCommand, Values)
              cnxn.commit()

cursor.close()
print('******************************** Complete *****************************')
driver.close()