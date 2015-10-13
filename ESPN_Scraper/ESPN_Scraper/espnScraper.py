__author__ = 'Ryan'

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import re
import csv
import os

year = '2015'

def Write_CSV(data, file_name):
	with open(file_name, "w") as csvfile:
		data_writer = csv.writer(csvfile, lineterminator = '\n')
		data_writer.writerows(data)

def Read_CSV(file_name):
	print "Reading " + str(file_name) + "..."
	data = []
	with open(file_name, "r") as csvfile:
		data_reader = csv.reader(csvfile)
		for row in data_reader:
			data.append(row)
	for i in range(0, len(data)):
		for j in range(0, len(data[i])):
			data[i][j] = re.sub("\"", "", data[i][j])
	return data

def addNewTeam(abbv,team_arr,team_abbvs):

	#team_arr = Read_CSV("../" + str(year) + " Stats/team.csv")
	#team_names = Read_CSV("../2014 Stats/team.csv")
	#team_arr = team_arr[1:]
	#team_abbvs = Read_CSV("../" + str(year) + " Stats/abbrevations.csv")

	num = 9000
	found= False
	numUsed = True
	while numUsed == True:
		found = False
		for line in team_arr:
			if int(line[0]) == num:
				found = True
				num += 1
				break
		numUsed = found
	print "ADDED " + abbv + " at " + str(num)
	line = [num,abbv,"999"]
	team_arr.append(line)
	#Write_CSV(team_arr,"../" +  str(year) + " Stats/team.csv")

def Find_Abbv(team_name,team_arr,team_abbvs):



	team_name = team_name.lower()
	team_name = team_name.replace(" ", "")
	team_name = team_name.replace("-", "")

	#if team_name == "charlotte":
	#	print "here"

	code = 0
	for team in team_arr:

		if team[1].lower().replace("-", "") == team_name or team[1].lower().replace(" ", "") == team_name:
			code = team[0]
			return (code, team[1], team_abbvs)
	if code == 0:
		for abbv in team_abbvs:
			if abbv[0].lower().replace("-", "") == team_name or abbv[0].lower().replace(" ", "") == team_name:
				code = abbv[1]
				return (code, abbv[0], team_abbvs)
	return Find_Abbv_Team(team_name, team_arr, team_abbvs)

# Changes an abbreviated team name to its team number
def Find_Abbv_Team(abbv, team_arr, abbv_arr):
	# Check if it is already matched
	if abbv_arr != 0:
		for team in abbv_arr:
			if abbv == team[0]:
				return (team[1], team[2], abbv_arr)
	team_sort = []
	for i in range(0, len(team_arr)):
		team_sort_tmp = [0] * 3					# naming correlation

		## TODO FLIP FOR ESPN
		team_sort_tmp[1] = team_arr[i][0]		# team number
		team_sort_tmp[2] = team_arr[i][1]		# team name
		#team_sort_tmp[1] = team_arr[i][1]		# team number
		#team_sort_tmp[2] = team_arr[i][0]		# team name
		abbv_ltrs = list(abbv)
		team_ltrs = list(team_arr[i][1])
		pos = 0
		tot = 0
		# Find the correlation in naming
		for j in range(0, len(abbv_ltrs)):
			ltr = abbv_ltrs[j]
			if ltr == "U" or None == re.search(r"[a-zA-Z]", ltr):
				continue
			inc = 0
			while None == re.search(ltr, team_ltrs[pos], re.IGNORECASE):
				inc += 1
				pos += 1
				if pos >= len(team_ltrs):
					break
			if pos >= len(team_ltrs):
				tot = 1000
				break
			else:
				tot += inc
		team_sort_tmp[0] = tot
		team_sort.append(team_sort_tmp)
	team_sort = sorted(team_sort, key=lambda arr: arr[0])
	# Check the sorted teams for the correct match
	i = 0

	while i < len(team_sort):
		print "\nGuess: " + str(abbv) + " = " + str(team_sort[i][2])
		user_in = raw_input("Enter 0 for incorrect match, 1 for correct match, or 2 for unknown: or 3 for add team to 9000+")
		for name in team_arr:
			if user_in == name[1]:
				if abbv_arr != 0:
					abbv_arr.append([abbv, name[0], name[1]])
					Write_CSV(abbv_arr,"../" +  str(year) + " Stats/abbrevations.csv")
				return (name[0], name[1], abbv_arr)
		if user_in == "":
			print "Please enter 1 or 0"
			continue
		if user_in == "":
			break
		if user_in == "1":
			break
		if user_in == "3":
			addNewTeam(abbv, team_arr, abbv_arr)
			#team_arr_new = Read_CSV("../" + str(year) + " Stats/team.csv")
			#team_names = Read_CSV("../2014 Stats/team.csv")
			#team_arr_new = team_arr[1:]
			#team_abbvs_new = Read_CSV("../" + str(year) + " Stats/abbrevations.csv")
			return Find_Abbv(abbv,team_arr,abbv_arr)
		if user_in == "2":
			print "The next option is " + str(team_sort[i + 1][2])
			continue
		i += 1
		if i == len(team_sort):
			i = 0
	if abbv_arr != 0:
		abbv_arr.append([abbv, team_sort[i][1], team_sort[i][2]])
		Write_CSV(abbv_arr,"../" +  str(year) + " Stats/abbrevations.csv")
	return (team_sort[i][1], team_sort[i][2], abbv_arr)

def crawl(year):

	team_arr = Read_CSV("../" + str(year) + " Stats/team.csv")
	#team_names = Read_CSV("../2014 Stats/team.csv")
	out_team_arr = []
	out_team_arr.append(team_arr[0])
	team_arr = team_arr[1:]
	team_abbvs = Read_CSV("../" + str(year) + " Stats/abbrevations.csv")

	newPath = "../" + str(year) + "/scraped_games"

	teams = pd.read_csv('ESPN_teams.csv')
	BASE_URL = 'http://espn.go.com/college-football/team/schedule/_/id/{0}/year/{1}/{2}'

	match_id = []
	dates = []
	home_team = []
	home_team_score = []
	visit_team = []
	visit_team_score = []

	for index, row in teams.iterrows():
		_team, url = row['team'], row['url']
		r = requests.get(BASE_URL.format(row['prefix_1'], year, row['prefix_2']))
		soup = BeautifulSoup(r.text, "html.parser")
		table = soup.find('table', {'class':'tablehead'})
		if not table:
			continue

		week = 0
		for row in table.find_all('tr')[1:]: # Remove header
			columns = row.find_all('td')
			#if 1 == 1:
			try:
				_home = True if columns[1].li.text == 'vs' else False
				_other_team = columns[1].find_all('a')[1].text
				_score = columns[2].a.text.split(' ')[0].split('-')
				_won = True if columns[2].span.text == 'W' else False
				match_id = columns[2].a['href'].split('?id=')[1]
				datestring = columns[0].text
				datestring = datestring.replace('Sept','Sep')
				d = datetime.strptime(datestring, '%a, %b %d')
				d = d.replace(year=int(year))
				date = d.strftime('%Y%m%d')


				home = _team if _home else _other_team
				(home_code, home_off, team_abbvs) = Find_Abbv(home, team_arr, team_abbvs)				# find home code
				visitor =_team if not _home else _other_team
				(visitor_code, visitor_off, team_abbvs) = Find_Abbv(visitor, team_arr, team_abbvs)	# find visitor code
				thisPath = newPath + "/week_" + str(week)
				if not os.path.exists(thisPath):
					os.makedirs(thisPath)
				filename = thisPath + "/" + str(visitor_code).zfill(4) + str(home_code).zfill(4) + date + ".txt"
				with open(filename, 'w') as f:
					f.write("Date: " + date + "\n")
					f.write("Home: " + home + " (" + str(home_code) + ")" + "\n")
					f.write("Away: " + visitor + " (" + str(visitor_code) + ")" + "\n")
					f.write("Week: " + str(week) + "\n")
					f.write("Box: " + "http://scores.espn.go.com/college-football/boxscore?gameId=" +match_id +"\n")
					f.write("Matchup: " + "http://scores.espn.go.com/college-football/matchup?gameId=" +match_id +"\n")
					f.write("PBP: " + "http://scores.espn.go.com/college-football/playbyplay?gameId=" +match_id +"\n")
					f.write("Drives: " + "http://scores.espn.go.com/college-football/drivechart?gameId=" +match_id +"\n")

					f.close()


			except Exception as e:
				pass # Not all columns row are a match, is OK
				print(e)

			week += 1
	out_team_arr = out_team_arr + team_arr
	Write_CSV(out_team_arr,"../" +  str(year) + " Stats/team.csv")
	'''
	dic = {'id': match_id, 'date': dates, 'home_team': home_team, 'visit_team': visit_team,
		'home_team_score': home_team_score, 'visit_team_score': visit_team_score}

	games = pd.DataFrame(dic).drop_duplicates(subset='id').set_index('id')
	games.to_csv('games.csv')
	'''



crawl(year)