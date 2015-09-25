__author__ = 'Ryan'

import csv
from ValidatePBP import ValidatePBP
from ESPN_Parser.BugCheckPBP import Check_Play
import math

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
	dict1 = buildDict(csv1)#csv.DictReader(csv1)
	dict2 = buildDict(csv2)#csv.DictReader(csv2)
	drive1Offsets = findGames(dict1)
	drive2Offsets = findGames(dict2)

	outDict =[]

	commonGames = getCommonGames(drive1Offsets,drive2Offsets)
	for game in commonGames:
		gameDict = []
		outPlay = False
		print "checking Game " + game
		index1 = drive1Offsets[game]
		index2 = drive2Offsets[game]






		play1 = dict1[index1 -1]
		play2 = dict2[index2 -1]

		game1 = []
		inc = -1
		while play1['Game Code'] == game and index1 + inc < len(dict1):
			DriveNum = play1['Drive Number']
			drive = []
			#while play1['Drive Number'] == DriveNum :
			game1.append(play1)
			inc += 1
			if index1 + inc > len(dict1) -1:
				break
			play1 = dict1[index1 + inc]
			#game1.append(drive)

		game2 = []
		inc = -1
		while play2['Game Code'] == game and index2  + inc < len(dict2):
			DriveNum = play2['Drive Number']
			drive = []
			#while play2['Drive Number'] == DriveNum:
			game2.append(play2)
			inc += 1
			if index2  + inc > len(dict2) -1:
				break
			play2 = dict2[index2 + inc]
			#game2.append(drive)


		playNum1 = 0
		playNum2 = 0

		FillDict = {}

		while playNum1 < len(game1):
			play1 = game1[playNum1]
			playFound = False
			ExtraPlays = []
			depth = 0
			game1Missed = []
			game2Missed = []

			while playNum2 < len(game2)  and depth < search_distance and not playFound:
				play2 = game2[playNum2]
				if playMatches(play1,play2):
					playFound = True

					for x in reversed(range(depth)):
						game1Missed.append(game2[playNum2 - x])
						print "Missing from Game 1 @ " + str(int(playNum2-x)) + ": " + game2[playNum2 - x]['Play Desc']
				#else:
					#print "passing here"
				#	pass #Debug hook
				depth += 1
				playNum2 +=1

			if playFound:
				if game1Missed or game2Missed:
					FillDict[str(len(gameDict))] = {}
					FillDict[str(len(gameDict))]['0'] = game1Missed
					FillDict[str(len(gameDict))]['1'] = game2Missed
				outPlay=mergePlays(play1,play2,outPlay)
				gameDict.append(outPlay)

			else:
				game2Missed.append(play1)
				print "Missing from Game 2 @ " + str(playNum1) + ": " + play1['Play Desc']
				playNum2 -= depth
			playNum1 += 1
		pass
		corGameDict = FindBestCombo(game1,game2,gameDict,FillDict)
		print "done with game"

		'''
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
								remove_play,bad_drive_sequence,bad_play_data =Check_Play(outPlay,play,False)
								if remove_play or bad_drive_sequence: #bad_play_data
									print "We won't add this, its messed up"
								else:
									outPlay = play
									outPlay['Recently Added'] = 1
									outDict.append(outPlay)
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


				print "Drive1 Play was not found in Drive2  Index:" + str(index1 + game1Offset )
				print play1['Play Desc']

				remove_play,bad_drive_sequence,bad_play_data =Check_Play(outPlay,play1,False)
				if remove_play or bad_drive_sequence: #bad_play_data
					print "We won't add this, its messed up"
				else:
					outPlay = play1
					outPlay['Recently Added'] = 1
					outDict.append(outPlay)
				game2Offset =  game2Offset - len(ExtraPlays) - 1

			else:
				## compare found Plays
				#diffPlays(play1,play2)
				outPlay=mergePlays(play1,play2,outPlay)
				if len(outDict) > 0:
					remove_play,bad_drive_sequence,bad_play_data =Check_Play(outDict[-1],outPlay,False)
					if remove_play or bad_drive_sequence : #bad_play_data
						if 'Recently Added' in outDict[-1]:
							outDict.remove(outDict[-1])
							print "**** Removing the play we just added, its not right, Testing without it*****"
							remove_play,bad_drive_sequence,bad_play_data =Check_Play(outDict[-1],outPlay,False)
							if remove_play or bad_drive_sequence:
								print "!!!!!WE STILL BROKEN!!!!!!"
						else:
							print "**** SOMETHING IS WRONG HERE*****"
				outDict.append(outPlay)

			game1Offset +=1
			if(index1 + game1Offset) < len(drive1):
				play1 = drive1[index1 + game1Offset]
			else:
				break
		'''
	return outDict

def FindBestCombo(game1,game2,commonDict,diffDict):
	numCombos = int(math.pow(2,len(diffDict)))
	for combo in range(numCombos) :
		binCombo = bin(combo)[2:].zfill(len(diffDict))
		MakeGameFromCombo(binCombo,commonDict,diffDict)

def MakeGameFromCombo(binCombo,commonDict,diffDict):
	outGame = commonDict
	offset = 0
	for diff in sorted(diffDict.iterkeys(),reverse = True):
		index = int(diff)
		binCombo,bit = binCombo[:-1],binCombo[-1]
		outGame[index:index] = diffDict[diff][bit]
	return outGame



def mergePlays(play1,play2,prev_play):
	return play1

	remove_play1,bad_drive_sequence1,bad_play_data1 =Check_Play(prev_play,play1,False)
	remove_play2,bad_drive_sequence2,bad_play_data2 =Check_Play(prev_play,play2,False)

	outplay = play2
	catergories = play1.keys()

	if prev_play == False:
		return outplay

	for catergory in catergories:
		if play1[catergory] != play2[catergory]:
			pass
			#if play1[catergory] == '':
			#	outplay[catergory] = play2[catergory]
			#elif play2[catergory] == '':
			#	outplay[catergory] = play1[catergory]
			if catergory == 'Yards Gained':#catergory == 'Spot' or
				if not bad_play_data2:
					outplay[catergory] = play2[catergory]
				else:
					outplay[catergory] = play1[catergory]
			if catergory == 'Play Desc':
				if play1['Play Type'] == 'Attempt':
					outplay[catergory] = play2[catergory]
				#print "DIF!"
	#Check_Play(prev_play,outplay,False)
	return outplay

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
	z4catergories_to_check = ['Offense Team Code','Down','Spot','Play Type','Distance','Completion']#,'Drive Number']
	retval = True
	if play1['Play Type'] == 'KICKOFF' and play2['Play Type'] == 'KICKOFF':
		if abs(int(play1['Kick Yards']) - int(play2['Kick Yards'])) < 2:
			return True
		return False
	elif play1['Play Type'] == 'FIELD GOAL' and play2['Play Type'] == 'FIELD GOAL':
		if abs(int(play1['Kick Yards']) - int(play2['Kick Yards'])) < 2:
			return True
		return False
	elif play1['Play Type'] == 'ATTEMPT' and play2['Play Type'] == 'ATTEMPT':
		return True
	#for catergory in catergories_to_check:
	#if catergory == 'Spot' or catergory =='Distance':

	Spot = True
	Distance = True
	Completion = True
	Penalty = True
	Down = True
	if play1['Spot'] != play2['Spot']:
		if abs(int(play1['Spot']) - int(play2['Spot'])) > 1:
			Spot = False
	if play1['Distance'] != play2['Distance']:
		if abs(int(play1['Distance']) - int(play2['Distance'])) > 1:
			Spot = False
	if play1['Play Type'] == 'PENALTY' or play2['Play Type'] == 'PENALTY':
		if int(play1['Penalty']) != int(play2['Penalty']):
			Penalty = False
	if play1['Completion'] != play2['Completion']:
		if int(play1['Penalty']) != 1 or int(play2['Penalty']) != 1:
			Completion =  False
	if play1['Down'] != play2['Down']:
		Down = False


	return Spot and Distance and Completion and Penalty and Down


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
	for (key) in set(list(dict2.keys())) & set(list(dict1.keys())):
		common.append(key)
		print (key + " Matches Both!")
	for (key) in set(list(dict2.keys())) ^ set(list(dict1.keys())):
		continue
		#print(key + " Only found in One DataSet")
	common = sorted(common)
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

CompESPN = ValidatePBP(path + 'play_TGS.csv',"2015 Stats/boxscore-stats.csv")
headers = []
outDrive = []
with open(path + 'play.csv') as csv1:  #ESPN
	with open(path +'ncaa/play.csv') as csv2:  #CFB
		outDrive = compareDrives(csv1,csv2)#,CompESPN,CompNCAA)
	csv1.seek(0)
	reader = csv.DictReader(csv1)
	headers = reader.fieldnames

with open(path + 'out_play.csv','w') as csvout:
	writer = csv.DictWriter(csvout,fieldnames=headers,extrasaction='ignore',lineterminator='\n')
	writer.writeheader()
	for line in outDrive:
		writer.writerow(line)

#writeCSV outplay.csv
#OutReport = ValidatePBP('outplay.csv',outbox)