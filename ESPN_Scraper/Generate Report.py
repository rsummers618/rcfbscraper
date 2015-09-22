

from os import listdir
from os.path import isdir, isfile, join
import re
import csv

year = 2015

def getConferenceCode(teamCode):
	with open(str(year) + " Stats/team.csv") as team_file:
		teams = csv.DictReader(team_file)
		for team in teams:
			if int(team['Team Code']) == int(teamCode):
				return team['Conference Code']
	print "CONFERENCE CODE NOT FOUND " + teamCode
	return -1


def getConferenceNameandSubDivision(conferenceCode):

	with open(str(year) + " Stats/conference.csv") as team_file:
		teams = csv.DictReader(team_file)
		for team in teams:
			if int(team['Conference Code']) == int(conferenceCode):
				return team['Name'],team['Subdivision']
	print "CONFERENCE NAME NOT FOUND " + conferenceCode
	return '-1','-1'


def getGames():
	gameDict = {}
	for week in range(1,17):
		path = str(year) + "/scraped_games/week_" + str(week) + "/"
		game_files = [f for f in listdir(path) if isfile(join(path, f))]



		for game_file in game_files:
			game_id = game_file[:-4]
			gameDict[game_id] ={}
			with open (path + game_file, "r") as f:
					data = f.read()
					# Get start URL
					m = re.search(r"PBP: (?P<url>\S+)", data,re.IGNORECASE)
					if ''.join(e for e in m.group("url") if e.isalnum()) == "httpscoresespngocom":
						continue
					gameDict[game_id]['PBP_link'] = m.group("url") + "&period=0"
					# Get date
					m = re.search(r"Date: (?P<date>\d+)", data,re.IGNORECASE)
					gameDict[game_id]['date'] = m.group("date")
					# Get home
					m = re.search(r"Home: (?P<team>\D+) \((?P<code>\d+)\)", data,re.IGNORECASE)
					gameDict[game_id]['home_code'] = m.group("code")
					gameDict[game_id]['home_name'] = m.group("team")
					# Get visitor
					m = re.search(r"Away: (?P<team>\D+) \((?P<code>\d+)\)", data,re.IGNORECASE)
					gameDict[game_id]['away_code'] = m.group("code")
					gameDict[game_id]['away_name'] = m.group("team")
					gameDict[game_id]['has_pbp'] = False

					gameDict[game_id]['away_conference_code'] = getConferenceCode(gameDict[game_id]['away_code'])
					gameDict[game_id]['away_conference'],gameDict[game_id]['away_subdivision'] = getConferenceNameandSubDivision(gameDict[game_id]['away_conference_code'])

					gameDict[game_id]['home_conference_code'] = getConferenceCode(gameDict[game_id]['home_code'])
					gameDict[game_id]['home_conference'],gameDict[game_id]['home_subdivision'] = getConferenceNameandSubDivision(gameDict[game_id]['home_conference_code'])

	return gameDict

def checkPBP(gameDict):
	path = str(year) + "/pbp/"
	game_files = [f for f in listdir(path) if isfile(join(path, f))]

	for game_file in game_files:
		game_id = game_file[:-4]
		if game_id in gameDict:
			gameDict[game_id]['has_pbp'] = True
		else:
			print "Not sure how this got here Game:" + game_id
	return gameDict

gameDict = getGames()
gameDict = checkPBP(gameDict)

for key in gameDict:
	if gameDict[key]['has_pbp'] == False:
		print gameDict[key]['away_name'] + " @ " + gameDict[key]['home_name']

