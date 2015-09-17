__author__ = 'Ryan'

import csv

year = 2015
search_distance = 5

def buildDict(csvfile):
	csvreader = csv.reader(csvfile)
	header = csvreader.next()
	outDict = []
	for line in csvreader:
		newDict = {}
		for x in range(len(line)):
			newDict[header[x]] = line[x]
		outDict.append(newDict)
	return outDict
def compareBoxScores(csv1,csv2):
	box1 = buildDict(csv1)#csv.DictReader(csv1)
	box2 = buildDict(csv2)#csv.DictReader(csv2)
	box1Offsets = findGames(box1)
	box2Offsets = findGames(box2)

	commonGames = getCommonGames(box1Offsets,box2Offsets)
	for game in commonGames:
		print "checking Game " + game
		index1 = box1Offsets[game]
		index2 = box2Offsets[game]

		game1 = box1[index1]
		game2 = box2[index2]

		commonStats = getCommonGames(game1,game2)
		for stat in commonStats:
			if game1[stat] != game2[stat]:
				print "Found a mismatch in box scores"

def compareDrives(csv1,csv2):
	drive1 = buildDict(csv1)#csv.DictReader(csv1)
	drive2 = buildDict(csv2)#csv.DictReader(csv2)
	drive1Offsets = findGames(drive1)
	drive2Offsets = findGames(drive2)

	commonGames = getCommonGames(drive1Offsets,drive2Offsets)
	for game in commonGames:
		print "checking Game " + game
		index1 = drive1Offsets[game]
		index2 = drive2Offsets[game]




		game1Offset = -1
		game2Offset = -2

		play1 = drive1[index1 + game1Offset]
		play2 = drive2[index2 + game2Offset]

		while play1['Game Code'] == game:
			matchFound = -1
			ExtraPlays = []
			game2Offset +=1
			if(index2 + game2Offset) < len(drive2):
				play2 = drive2[index2 + game2Offset]
			else:
				break

			depth = 0
			while play2['Game Code'] == game and matchFound == -1 and depth < search_distance:
				aplay1desc = play1['Play Desc']
				aplay2desc = play2['Play Desc']
				if playMatches(play1,play2):
					#print "play found"
					matchFound = index2
					if len(ExtraPlays) > 0:
						print "Drive2 Plays not found in Drive1  End Index:" + str(index2 + game2Offset + 2)
						for play in ExtraPlays:
							if play['Play Type'] != 'Attempt' or play['Play Type'] != '':
								print play['Play Desc']
						#game2Offset =  game2Offset# - len(ExtraPlays)
				else:
					ExtraPlays.append(play2)
					game2Offset +=1
					if(index2 + game2Offset) < len(drive2):
						play2 = drive2[index2 + game2Offset]
					else:
						break
					depth += 1
			if matchFound == -1:

				if play1['Play Type'] != 'Attempt' or play['Play Type'] != 'Attempt':
					print "Drive1 Play was not found in Drive2  Index:" + str(index1 + game1Offset )
					print play1['Play Desc']
				game2Offset =  game2Offset - len(ExtraPlays) - 1

			else:
				## compare found Plays
				diffPlays(play1,play2)


			game1Offset +=1
			if(index1 + game1Offset) < len(drive1):
				play1 = drive1[index1 + game1Offset]
			else:
				break


def diffPlays(play1,play2):
	catergories_to_check = ['Spot','Play Type','Yards Gained','Off Touchdown','Def Touchdown','First Down','Completion','Interception','Fumble','Fumble Lost','Kick Good','TwoPt Good','Safety','Kick Yards',
							'Touchback','Kickoff OOB','Kickoff Onsides','Kick Blocked','Penalty','Penalty Type','No Play']#,'Rusher','Passer','Receiver','Kicker','Forced_Fum','Interceptor','Sacker','Extra Pt Att']

	DiffString = ''
	diff = False
	for catergory in catergories_to_check:
		if play1[catergory] != play2[catergory]:
			diff = True
			DiffString += " " + catergory + ": " + str(play1[catergory]) + " vs " + str(play2[catergory])
			#print "Plays don't match exactly " + play1['Play Desc'] + play2['Play Desc']

	#retval = True
	#for catergory in catergories_to_check:

		#if play1[catergory] != play2[catergory]:
			#retval = False
	#if diff == True:
	#	print "Plays don't match exactly " + play1['Play Desc'] + play2['Play Desc']
	#	print DiffString

	return diff

def playMatches(play1,play2):
	catergories_to_check = ['Offense Team Code','Down','Spot']#,'Drive Number']
	retval = True
	if play1['Play Type'] == 'KICKOFF' and play2['Play Type'] == 'KICKOFF':
		return True
	if play1['Play Type'] == 'FIELD GOAL' and play2['Play Type'] == 'FIELD GOAL':
		return True
	for catergory in catergories_to_check:
		if catergory == 'Spot' or catergory =='Distance':
			if play1[catergory] != play2[catergory]:
				try:
					if abs(int(play1[catergory]) - int(play2[catergory])) > 2:
						retval = False
				except:
					retval = False

		elif play1[catergory] != play2[catergory]:
			retval = False


	return retval


def findGames(reader):
	outDict = {}
	index = 1
	for line in reader:
		if not outDict.has_key(line['Game Code']):
			outDict[line['Game Code']] = index
		index +=1
	return outDict

def getCommonGames(dict1,dict2):
	common = []
	for (key) in set(list(dict1.keys())) & set(list(dict2.keys())):
		common.append(key)
		print (key + " Matches Both!")
	for (key) in set(list(dict1.keys())) ^ set(list(dict2.keys())):
		continue
		#print(key + " Only found in One DataSet")
	return common




def compareBoxScores(csv1,csv2):
	return
'''
with open('boxESPN') as csv1:
	with open('boxNCAA') as csv2:
		with open('boxRef') as csv3:
			outBox = compareBox(csv1,csv2,csv3)

CompESPN = ValidatePBP('ESPNplay.csv',outbox)
CompNCAA = ValidatePBP('ESPNplay.csv',outbox)
CompCFB = ValidatePBP('CFBplay.csv',outbox)

'''


path = "ESPN_Parser/" + str(year) + " Stats temp/"

with open(path + 'play.csv') as csv1:  #ESPN
	with open(path +'ncaa/play.csv') as csv2:  #CBS
		outDrive = compareDrives(csv1,csv2)#,CompESPN,CompNCAA)

#writeCSV outplay.csv
#OutReport = ValidatePBP('outplay.csv',outbox)