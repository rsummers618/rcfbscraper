

from os import listdir
from os.path import isdir, isfile, join
from ValidatePBP import *
from CrossCheck import GenAccuracyScore
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
					gameDict[game_id]['espn_pbp'] = False
					gameDict[game_id]['ncaa_pbp'] = False

					gameDict[game_id]['away_conference_code'] = getConferenceCode(gameDict[game_id]['away_code'])
					gameDict[game_id]['away_conference'],gameDict[game_id]['away_subdivision'] = getConferenceNameandSubDivision(gameDict[game_id]['away_conference_code'])

					gameDict[game_id]['home_conference_code'] = getConferenceCode(gameDict[game_id]['home_code'])
					gameDict[game_id]['home_conference'],gameDict[game_id]['home_subdivision'] = getConferenceNameandSubDivision(gameDict[game_id]['home_conference_code'])

	return gameDict

def checkPBP(gameDict):
	path = "ESPN_Parser/" + str(year) + " Stats temp/"
	ncaa = path + '/ncaa/play.csv'
	espn = path + 'play.csv'

	with open(ncaa) as ncaaCsv:
		reader = csv.DictReader(ncaaCsv)
		game_id = 0
		for line in reader:
			game_id = line['Game Code']
			if 0 != game_id:
				if game_id in gameDict:
					gameDict[game_id]['ncaa_pbp'] = True

	with open(espn) as espnCsv:
		reader = csv.DictReader(espnCsv)
		game_id = 0
		for line in reader:
			game_id = line['Game Code']
			if 0 != game_id:
				if game_id in gameDict:
					gameDict[game_id]['espn_pbp'] = True


	'''
	game_files = [f for f in listdir(path) if isfile(join(path, f))]

	for game_file in game_files:
		game_id = game_file[:-4]
		if game_id in gameDict:
			gameDict[game_id]['has_pbp'] = True
		else:
			print "Not sure how this got here Game:" + game_id
	'''
	return gameDict

def GenerateHTML(gameDict, diffDict):
	f = open('report.html','w+')
	f.write('<body>') # python will convert \n to os.linesep
	for key in gameDict:
		game = gameDict[key]
		header = "<h2>" + game['away_name'] + " @ " + game['home_name'] + " : on " + game['date']
		subheader = ''
		table = ''
		if game['espn_pbp'] == True and game['ncaa_pbp'] == True:
			subheader += "PBP Data From: ESPN & NCAA"
		elif game['espn_pbp'] == True:
			subheader += "PBP Data From: ESPN"
		elif game['ncaa_pbp'] == True:
			subheader += "PBP Data From: NCAA"
		else:
			subheader += "PBP Data From: (NONE)"
		if key in diffDict:
			table,accuracy = GenerateStatTable(game,diffDict[key],f)

		f.write(header + accuracy + "</h2>" +  subheader + table)
	f.write('</b>')
	f.close() # you can omit in most cases as the destructor will call it

def GenerateStatTable(game,stats,f):
	table = ''
	try:

		#f.write("<tr>")
		accuracyString = ''
		headerString = "<th> Team </th>"
		homeString ="<tr><td>" + game['home_name'] + "</td>"
		awayString ="<tr><td>" + game['away_name'] + "</td>"

		awayStats = stats[game['away_code']]
		homeStats = stats[game['home_code']]
	except:
		table += " - Key Error, PBP data probably has wrong TeamID"
		return '',''
	table +="<table style=\"width:100%\" border=\"1\">"
	ignore_list = ['Red Zone Att','Tackle For Loss Yard','QB Hurry','Kickoff Out-Of-Bounds','Def 2XP Made',	'Red Zone', 'Kickoff Onside','Misc Ret TD','Def 2XP Att','1st Down Penalty','Misc Ret',
				   'Tackle For Loss','Tackle Solo',	'Pass Broken Up']
	for stat in awayStats:
		if stat in ignore_list:
			continue
		headerString += "<th>" + stat + "</th>"
		if int(homeStats[stat]) == 0:
			homeString += "<td>" + str(homeStats[stat]) + "</td>"
		else:
			homeString += "<td><b>" + str(homeStats[stat]) + "</b></td>"
		if int(awayStats[stat]) == 0:
			awayString += "<td>" + str(awayStats[stat]) + "</td>"
		else:
			awayString += "<td><b>" + str(awayStats[stat]) + "</b></td>"
	#headerString += "</tr>"
	homeString +="</tr>"
	awayString +="</tr>"
	if len(awayStats) > 0 and len(homeStats) > 0:
		accuracyScore = GenAccuracyScore(homeStats) + GenAccuracyScore(awayStats)
		accuracyScore = (2000 -accuracyScore)/20
		### 66FF00 to 660000
		if accuracyScore < 0:
			greenColorHex = '00'
			redColorHex = 'FF'
			accuracyScore = 0
		else:
			greenColorHex =format(int(2.55*accuracyScore), 'x').zfill(2)
			redColorHex = format(int(255 - (2.55*accuracyScore)), 'x').zfill(2)
		fontColorHex = redColorHex +greenColorHex+'00'

		fontColorHex = str(fontColorHex)
		accuracyString = " Accuracy Score = <font color=\"" + fontColorHex +  "\">" + str(accuracyScore) + "</font>"

		#table = accuracyString + table
	table +=headerString
	table +=homeString
	table +=awayString
	table +="</table>"
	return table, accuracyString



######## MAIN ############
gameDict = getGames()
gameDict = checkPBP(gameDict)

diffDict = ValidatePBP('ESPN_Parser/' + str(year) + ' Stats temp/out_play_TGS.csv',#ncaa/play_TGS.csv',
			str(year) +' Stats/boxscore-stats.csv')

#for key in gameDict:
#	if gameDict[key]['espn_pbp'] == False and gameDict[key]['ncaa_pbp'] == False:
		#print gameDict[key]['away_name'] + " @ " + gameDict[key]['home_name']
	#else:
	#	compareGame

GenerateHTML(gameDict, diffDict)
