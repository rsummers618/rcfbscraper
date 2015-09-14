__author__ = 'Ryan'

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
#from unidecode import unidecode
import unicodedata


url = "http://espn.go.com/college-football/teams"
r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")
# tables = soup.findAll('a', href=re.compile('^http://espn.go.com/ncf/teams/schedule\?teamId='))
tables = soup.find_all("ul", class_="medium-logos")

teams = []
prefix_1 = []
prefix_2 = []
teams_urls = []
for table in tables:
	lis = table.find_all("li")
	for li in lis:
		info = li.h5.a
		teams.append(unicodedata.normalize('NFD',info.text).encode('ascii', 'ignore'))
		url = info["href"]

		teams_urls.append(unicodedata.normalize('NFD',url).encode('ascii', 'ignore'))

		prefix_1.append(unicodedata.normalize('NFD', url.split("/")[-2]).encode('ascii', 'ignore'))
		prefix_2.append(unicodedata.normalize('NFD', url.split("/")[-1]).encode('ascii', 'ignore'))

dic = {"url": teams_urls, "prefix_2": prefix_2, "prefix_1": prefix_1}
teams = pd.DataFrame(dic, index=teams)
teams.index.name = "team"
teams.to_csv("ESPN_teams.csv")

#for index, row in teams.iterrows():
#    url = row['url']
#    print index, url