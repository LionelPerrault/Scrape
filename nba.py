import openpyxl
from ast import Return
from asyncio.windows_events import NULL
import os
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
# import pyodbc 
from time import gmtime, strftime
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
import time
import random
import datetime
from selenium.webdriver.chrome.service import Service
import os
import wget
import zipfile
import pytz
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# # get the latest chrome driver version number
# url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
# response = requests.get(url)
# version_number = response.text

# # build the donwload url
# download_url = "https://chromedriver.storage.googleapis.com/" + version_number +"/chromedriver_win32.zip"

# # download the zip file using the url built above
# latest_driver_zip = wget.download(download_url,'chromedriver.zip')

# # extract the zip file
# with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
#     zip_ref.extractall() # you can specify the destination folder path here
# # delete the zip file downloaded above
# os.remove(latest_driver_zip)

# server = 'sql5030.smarterasp.net'
# database = 'DB_A17D64_trinovitech'
# username = 'DB_A17D64_trinovitech_admin'
# password = 'Schmuck@dmin1!'
# cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password + ';Trusted_Connection=no')
# cursor = cnxn.cursor()
# positions = ['G', 'PG', 'SG', 'F', 'SF', 'PF', 'C']

# todays_date = date.today() 
# statDate_url = str(todays_date).replace("-", "")
# statYear = todays_date.strftime("%Y")
# statDate = todays_date.strftime("%Y-%m-%d")

# statDate_url = "20220412"
# statYear = "2022"
# statDate ="2022-04-12"

# url = 'https://live.draftkings.com/sports/nba/seasons/2022/date/'+ statDate_url +'/games/all'
url = "https://www.sec.gov/edgar/search/#/q=SEC"
# url = "https://www.realtor.com/realestateandhomes-search/Security-Widefield_CO"
  
print('******************************** Start *****************************')

######## DEPENDING ON ENVIRONMENT, MIGHT NEED TO COMMENT OUT ABOVE AND USE BELOW DRIVER GET ################

# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")
# chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)

result_data = []
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--incognito")
chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
]
chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get(url)
time.sleep(5)
driver.delete_all_cookies()

items_filetype = driver.find_elements(By.CSS_SELECTOR, "td.filetype")
items_filed = driver.find_elements(By.CSS_SELECTOR, "td.filed")
items_enddate = driver.find_elements(By.CSS_SELECTOR, "td.enddate")
items_entity_name = driver.find_elements(By.CSS_SELECTOR, "td.entity-name")
items_cik = driver.find_elements(By.CSS_SELECTOR, "td.cik")
items_location = driver.find_elements(By.CSS_SELECTOR, "td.biz-location")
items_incorporated = driver.find_elements(By.CSS_SELECTOR, "td.incorporated")
items_fileNum = driver.find_elements(By.CSS_SELECTOR, "td.file-num a")
items_filmNum = driver.find_elements(By.CSS_SELECTOR, "td.film-num")


shortest_list_length = min(
    len(items_filetype),
    len(items_filed),
    len(items_enddate),
    len(items_entity_name),
    len(items_cik),
    len(items_location),
    len(items_incorporated),
    len(items_fileNum),
    len(items_filmNum)
)

def sub_url_fetch():
    sub_chrome_options = webdriver.ChromeOptions()
    sub_chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--incognito")
    sub_chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.142 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    ]
    sub_chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')

    sub_service = Service(ChromeDriverManager().install())

    sub_driver = webdriver.Chrome(service=sub_service, options=sub_chrome_options)
    sub_url = items_fileNum[i].parent.current_url
    sub_driver.get(sub_url)
    time.sleep(5)
    sub_driver.delete_all_cookies()
    company_name = sub_driver.find_element(By.CSS_SELECTOR, "span.companyName").text
    mail_address_infos = sub_driver.find_element(By.CSS_SELECTOR, "div.mailer")[1]
    return [company_name, mail_address_infos]

for i in range(shortest_list_length):
    sub_data = sub_url_fetch()  #testing
    row_data = [items_filetype[i].text, items_filed[i].text, items_enddate[i].text, items_entity_name[i].text, items_cik[i].text, items_location[i].text, items_incorporated[i].text, items_fileNum[i].text, items_filmNum[i].text] 
    result_data.append(row_data)


# items = driver.find_elements(By.CSS_SELECTOR, "div.BasePropertyCard_propertyCardWrap__30VCU")
# for item in items:
#   sub_item = item.find_element(By.CSS_SELECTOR, "div > div:last-child > div:last-child")
#   data_container = sub_item.find_elements(By.CSS_SELECTOR, "div")
#   conditions = sub_item.find_elements(By.CSS_SELECTOR, "ul").text
#   item_row = [data_container[0].text, data_container[1].text, data_container[2].text, conditions]
#   data.append(item_row)


wb = openpyxl.Workbook()
ws = wb.active

for row_num, row_data in enumerate(result_data[0:], start=1):
    for col_num, cell_value in enumerate(row_data, 1):
        ws.cell(row=row_num, column=col_num, value=cell_value)
  
wb.save(filename="scraped_data.xlsx")
driver.quit()


"""

i = 0
total_len = len(items)
carousel_len = 5
j = 1
try:
  elem = driver.find_element(By.CSS_SELECTOR, "main ul").find_element(By.XPATH, "./following-sibling::span")
except NoSuchElementException:
  elem = ""
time.sleep(10)
players = driver.find_elements(By.CSS_SELECTOR, "div#leaderboardScroller > article")
if(len(players) == 1 and players[0].text == "No players available."):
  print(players[0].text)
else:
  for player in players:
    playerName = player.find_element(By.CSS_SELECTOR, " h2").text
    pos_salary = player.find_element(By.CSS_SELECTOR, " div > div > div:first-child > div > h2").find_element(By.XPATH, "./following-sibling::div").text
    expand_btn = player.find_element(By.CSS_SELECTOR, " button")
    playerPos = pos_salary.split("-")[0].strip()
    if(len(pos_salary.split("-")) > 1):
      Salary = pos_salary.split("-")[1].strip().replace('$', '').replace(',', '')
    else:
      Salary = ""    
    playerTeam = player.find_element(By.CSS_SELECTOR, " div > div > div:first-child > div > h2").find_element(By.XPATH, "./following-sibling::div").find_element(By.XPATH, "./following-sibling::div").text.split("(")[0].strip()
    if(playerTeam == "GS"):
          playerTeam = "GSW"
    elif (playerTeam == "NO" ):
          playerTeam = 'NOP'
    elif (playerTeam == "NY" ):
          playerTeam = 'NYK'
    elif (playerTeam == "PHO" ):
          playerTeam = 'PHX'
    elif (playerTeam == "SA" ):
          playerTeam = 'SAS'
    else:
      playerTeam = playerTeam   
    FPTS = player.find_element(By.CSS_SELECTOR, " h3").text.strip()
    imgLink = player.find_element(By.CSS_SELECTOR, " img").get_attribute("src")
    
    MIN = NULL
    PTS = NULL
    REB = NULL
    AST = NULL
    ThreePM = NULL
    STL = NULL
    BLK = NULL
    TO = NULL
    PF = NULL

    try:
      expand_btn.click()
      time.sleep(1)
      MIN = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:first-child > div:last-child > div:first-child > div:last-child").text
      PTS = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:first-child > div:last-child > div:nth-child(2) > div:last-child").text
      REB = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:first-child > div:last-child > div:nth-child(3) > div:last-child").text
      AST = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:first-child > div:last-child > div:nth-child(4) > div:last-child").text
      ThreePM = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:first-child > div:last-child > div:nth-child(5) > div:last-child").text

      STL = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:last-child > div:last-child > div:first-child > div:last-child").text
      BLK = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:last-child > div:last-child > div:nth-child(2) > div:last-child").text
      TO = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:last-child > div:last-child > div:nth-child(3) > div:last-child").text
      PF = player.find_element(By.CSS_SELECTOR, " div > div:last-child > div:last-child > div:last-child > div:nth-child(4) > div:last-child").text      
    except WebDriverException as e:     
      continue

    print(playerName, playerPos, Salary, playerTeam, FPTS, imgLink, MIN, PTS, REB, AST, ThreePM, STL, BLK, TO, PF)
    SqlSelectCommand = ("SELECT * FROM dbo.NBAFantasyStats WHERE playerName=? and StatDate=?")
    Values = [playerName, statDate]
    row = cursor.execute(SqlSelectCommand, Values)
    if(len(row.fetchall()) == 0):
      SQLInsertCommand = ("INSERT INTO dbo.NBAFantasyStats (NBAYear, playerName, StatDate, playerPos, playerTeam, Salary, FPTS, MIN, PTS, REB, AST, ThreePM, STL, BLK, [TO], PF) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
      Values = [statYear, playerName, statDate, playerPos, playerTeam, Salary, FPTS, MIN, PTS, REB, AST, ThreePM, STL, BLK, TO, PF]   
      cursor.execute(SQLInsertCommand,Values)
    else:
      Values = [FPTS, Salary, imgLink, MIN, PTS, REB, AST, ThreePM, STL, BLK, TO, PF, playerName, statDate]  
      SQLUpdateCommand = ("UPDATE dbo.NBAFantasyStats SET FPTS=?, Salary=?, imgLink=?, MIN=?, PTS=?, REB=?, AST=?, ThreePM=?, STL=?, BLK=?, [TO]=?, PF=? WHERE playerName=? and StatDate=?")
      cursor.execute(SQLUpdateCommand, Values)
    cnxn.commit()
  
print('******************************** Board *****************************')

for item in items:
  i = i + 1
  if(j * carousel_len < total_len and i == carousel_len):
    AwayTeam = item.find_element(By.CSS_SELECTOR, "div > a > div > div > div:first-child > div > span > span").text
    HomeTeam = item.find_element(By.CSS_SELECTOR, "div > a > div > div > div:last-child > div > span > span").text
    MatchupKey = statDate_url + AwayTeam + HomeTeam
    try:
      ScoreAwayTotal = item.find_element(By.CSS_SELECTOR, "div > a > div > div > div:first-child > div > span:last-child").text
    except NoSuchElementException:
      ScoreAwayTotal = ""
    try:
      ScoreHomeTotal = item.find_element(By.CSS_SELECTOR, "div > a > div > div > div:last-child > div > span:last-child").text
    except NoSuchElementException:
      ScoreHomeTotal = ""
    if(AwayTeam == ScoreAwayTotal): ScoreAwayTotal = ""
    if(HomeTeam == ScoreHomeTotal): ScoreHomeTotal = ""
    Season = item.find_element(By.CSS_SELECTOR, "div > a > div > div:last-child > div").text
    if(elem != ""): elem.click()
    time.sleep(3)
    j = j + 1
    i = 0
  else:  
    AwayTeam = item.find_element(By.CSS_SELECTOR, "div > a > div > div:first-child > div:first-child > div > span > span").text
    HomeTeam = item.find_element(By.CSS_SELECTOR, "div > a > div > div:first-child > div:last-child > div > span > span").text
    try:
      ScoreAwayTotal = item.find_element(By.CSS_SELECTOR, "div > a > div > div:first-child > div:first-child > div > span:last-child").text
    except NoSuchElementException:
      ScoreAwayTotal = ""
    try:
      ScoreHomeTotal = item.find_element(By.CSS_SELECTOR, "div > a > div > div:first-child > div:last-child > div > span:last-child").text
    except NoSuchElementException:
      ScoreHomeTotal = ""
    if(AwayTeam == ScoreAwayTotal): ScoreAwayTotal = ""
    if(HomeTeam == ScoreHomeTotal): ScoreHomeTotal = ""
    if AwayTeam == "GW" :
              AwayTeam = "GSW"
    elif AwayTeam == "NO" :
          AwayTeam  = "NOP"
    elif AwayTeam == "NY" :
          AwayTeam = "NYK"
    elif AwayTeam == "PHO" :
          AwayTeam = "PHX"
    elif AwayTeam == "SA" :
          AwayTeam = "SAS"
    else : AwayTeam = AwayTeam
    if HomeTeam == "GW" :
          HomeTeam = "GSW"
    elif HomeTeam == "NO" :
          HomeTeam  = "NOP"
    elif HomeTeam == "NY" :
          HomeTeam = "NYK"
    elif HomeTeam == "PHO" :
          HomeTeam = "PHX"
    elif HomeTeam == "SA" :
          HomeTeam = "SAS"
    else : HomeTeam = HomeTeam    
    MatchupKey = statDate_url + AwayTeam + HomeTeam

    Season = item.find_element(By.CSS_SELECTOR, "div > a > div > div:last-child > div").text
  # Date = datetime.datetime.strptime(statDate_url, "%Y%m%d").strftime("%a %b %d")
  Date = datetime.datetime.strptime(statDate_url, "%Y%m%d")

  print(MatchupKey, AwayTeam, HomeTeam, ScoreAwayTotal, ScoreHomeTotal, Date, Season)
  SqlSelectCommand = "SELECT * FROM dbo.Board WHERE MatchupKey='" + MatchupKey + "'"
  row = cursor.execute(SqlSelectCommand)
  if(len(row.fetchall()) == 0):
    stripTime = Season[4:]
    stripTime = datetime.datetime.strptime(stripTime, '%I:%M %p')
    game24hrTime = stripTime.strftime("%H:%M")
    GameTime = statDate + " " + game24hrTime
    format  = "%Y-%m-%d %H:%M"
    localGameTime = datetime.datetime.strptime(GameTime, format)
    utcGameTime = localGameTime.astimezone(pytz.UTC)
    dtGameTime = utcGameTime.strftime(format)
    print(dtGameTime)
    SQLInsertCommand = ("INSERT INTO dbo.Board (MatchupKey, fkSportKey, Date, AwayTeam, HomeTeam, ScoreAwayTotal, ScoreHomeTotal, Season) VALUES (?,?,?,?,?,?,?,?)")    
    Values = [MatchupKey, 2, dtGameTime, AwayTeam, HomeTeam, ScoreAwayTotal, ScoreHomeTotal, Season]   
    cursor.execute(SQLInsertCommand,Values)
  else:
    SQLUpdateCommand = "UPDATE dbo.Board SET ScoreAwayTotal = '" + ScoreAwayTotal + "', ScoreHomeTotal = '" + ScoreHomeTotal + "', Season = '" + Season + "' WHERE MatchupKey = '" + MatchupKey + "'"
    cursor.execute(SQLUpdateCommand)
  cnxn.commit()
print('******************************** Complete *****************************')
cursor.close()        
driver.close()

"""