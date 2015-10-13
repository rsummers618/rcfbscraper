__author__ = 'Ryan'

import csv
from ESPN_Parser.Team_Game_Statistics import Team_Game_Statistics
from ValidatePBP import ValidatePBP
from ValidatePBP import compareGame
from ESPN_Parser.BugCheckPBP import Check_Play
from ESPN_Parser.BugCheckPBP import Bug_Check
from ESPN_Parser.Team_Game_Statistics import *
import math
import copy

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

	commonGames,diffGames = getCommonGames(box1Offsets,box2Offsets)
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

def compareDrives(csv1,csv2,BoxScoresReader,tgsout):

	TGSOut = csv.writer(tgsout,lineterminator='\n')
	temp  = Team_Game_Statistics(0,0)
	TGSOut.writerow(temp.Header())

	BoxScores = []

	for row in BoxScoresReader:
			BoxScores.append(row)
	for i in range(0, len(BoxScores)):
		for j in range(0, len(BoxScores[i])):
			BoxScores[i][j] = re.sub("\"", "", BoxScores[i][j])


	dict1 = buildDict(csv1)#csv.DictReader(csv1)
	dict2 = buildDict(csv2)#csv.DictReader(csv2)
	drive1Offsets = findGames(dict1)
	drive2Offsets = findGames(dict2)

	outDict =[]

	commonGames,diffGames1,diffGames2 = getCommonGames(drive1Offsets,drive2Offsets)
	#commonGames = commonGames[-2:-1]
	#commonGames = commonGames[102:103]


	for game in commonGames:

		game1 = MakeGameFromPBP(game,dict1,drive1Offsets)
		game2 = MakeGameFromPBP(game,dict2,drive2Offsets)
		corGameDict,TGS =  ProcessCommonGame(game1,game2,game,BoxScores)
		for line in TGS:
			TGSOut.writerow(line)
		outDict = outDict + corGameDict


	for game in diffGames1:

		corGameDict,TGS = ProcessDiffGame(drive1Offsets,dict1,game,BoxScores)
		for line in TGS:
			TGSOut.writerow(line)
		outDict = outDict + corGameDict

	for game in diffGames2:

		corGameDict,TGS = ProcessDiffGame(drive2Offsets,dict2,game,BoxScores)
		for line in TGS:
			TGSOut.writerow(line)
		outDict = outDict + corGameDict

	return outDict

def ProcessDiffGame(drive1Offsets,dict1,game,BoxScores):
	inGame = MakeGameFromPBP(game,dict1,drive1Offsets)
	outGame = copy.deepcopy(inGame)
	outCombo,num_bad_sequence,num_bad_data = Bug_Check(ConvertDictToGame(outGame),True)
	return ProcessCommonGame(inGame, ConvertGameToDict(outCombo),game,BoxScores)



def MakeGameFromPBP(game,dict,driveOffsets):
	index1 = driveOffsets[game]
	play1 = dict[index1 -1]
	gameOut = []
	inc = -1
	while play1['Game Code'] == game and index1 + inc < len(dict):
		DriveNum = play1['Drive Number']
		drive = []
		#while play1['Drive Number'] == DriveNum :
		gameOut.append(play1)
		inc += 1
		if index1 + inc > len(dict) -1:
			break
		play1 = dict[index1 + inc]
		#game1.append(drive)
	return gameOut

def ProcessCommonGame(game1,game2,game,BoxScores):
	gameDict = []
	outPlay = False
	print "checking Game " + game




	playNum1 = 0
	playNum2 = 0

	FillDict = {}

	game1Missed = []
	game2Missed = []

	while playNum1 < len(game1):
		play1 = game1[playNum1]
		playFound = False
		ExtraPlays = []
		depth = 0


		while playNum2 < len(game2)  and depth < search_distance and not playFound:
			play2 = game2[playNum2]
			if playMatches(play1,play2):
				playFound = True

				for x in reversed(range(depth)):
					game1Missed.append(game2[playNum2 - x-1])
					print "Missing from Game 1 @ " + str(int(playNum2-x-1)) + ": " + game2[playNum2 - x-1]['Play Desc']
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
				game1Missed = []
				game2Missed = []
			outPlay=mergePlays(play1,play2,outPlay)
			outPlay['G1Index'] = playNum1
			outPlay['G2Index'] = playNum2 -1
			gameDict.append(outPlay)

		else:
			game2Missed.append(play1)
			print "Missing from Game 2 @ " + str(playNum1) + ": " + play1['Play Desc']
			playNum2 -= depth
		playNum1 += 1
	pass


	boxScore = []
	for line in BoxScores:
		if line[1] == game:
			boxScore.append(line)
			if len(boxScore) >= 2:
				break
	corGameDict,TGS = FindBestCombo(game1,game2,gameDict,FillDict,boxScore)
	corGameDict = CleanUpGame(corGameDict)
	return corGameDict,TGS


def CleanUpGame(gameDict):
	prevPlay = False
	playNum = 1
	for play in gameDict:
		try:
			play["Offense Team Code"] = play.pop('Offense')
			play["Defense Team Code"] = play.pop('Defense')
			play["Offense Points"] = play.pop('Off Points')
			play["Defense Points"] = play.pop('Def Points')
		except:
			pass
		play["Play Number"] = playNum



		playNum +=1

		if prevPlay:
			if play['Drive Number'] == '':
				play['Drive Number'] == prevPlay['Drive Number']
			if prevPlay['Drive Start'] < play['Drive Start'] and prevPlay['Period Number'] == play['Period Number']:
				play['Drive Start'] = prevPlay['Drive Start']
			try:
				if prevPlay['Drive Number'] == play['Drive Number']:
					play['Drive Play'] = int(prevPlay['Drive Play']) - int(prevPlay['No Play']) + 1
				else:
					play['Drive Play'] = 1
			except:
				play['Drive Play'] = 1
		else:
			play['Drive Play'] = 1


		prevPlay = play
	return gameDict



def ConvertDictToGame(gameDict):
	outClass = []
	for line in gameDict:
		tempdict = {}
		for key in line:
			try:
				line[key] = int (line[key])
			except:
				pass

			if key == "Offense Team Code":
				tempdict["Offense"] = line[key]
			elif key == "Defense Team Code":
				tempdict["Defense"] = line[key]
			elif key == "Offense Points":
				tempdict["Off_Points"] = line[key]
			elif key == "Defense Points":
				tempdict["Def_Points"] = line[key]
			else:
				tempdict[key.replace (" ", "_")] = line[key]


		outClass.append(objectview(tempdict))
	return outClass

class objectview(object):
	def __init__(self, d):
		self.__dict__ = d

def ConvertGameToDict(game):
	outDict = []
	for line in game:
		curDict = {}
		for key, value in line.__dict__.items():
			if not key.startswith('__') and not callable(key):

				if key == "Offense":
					curDict["Offense Team Code"] = str(value)
					curDict.pop(key,None)
				elif key == "Defense":
					curDict["Defense Team Code"] = str(value)
					curDict.pop(key,None)
				elif key == "Off_Points":
					curDict["Offense Points"] = str(value)
					curDict.pop(key,None)
				elif key == "Def_Points":
					curDict["Defense Points"] = str(value)
					curDict.pop(key,None)
				else:
					curDict[key.replace ("_", " ")] = str(value)
				#curDict ={key:value for key, value in line.__dict__.items() if not key.startswith('__') and not callable(key)}
		outDict.append(curDict)
	return outDict

def GameAccuracyScore(gameClass,boxScore):

	allTGS = []
	prev_game_code = 0

	visitor_code = int(math.floor(float(gameClass[0].Game_Code)/1e12))
	home_code = int(math.floor(float(gameClass[0].Game_Code)/1e8)) % 1e4
	home_tgs = Team_Game_Statistics(gameClass[0].Game_Code, home_code)
	visitor_tgs = Team_Game_Statistics(gameClass[0].Game_Code, visitor_code)

	for play in gameClass:

		if play.Offense == home_tgs.Team_Code:
			home_tgs.Extract_Play_Offense(play,visitor_tgs)
		elif play.Offense == visitor_tgs.Team_Code:
			visitor_tgs.Extract_Play_Offense(play,home_tgs)

	allTGS.append(home_tgs)
	allTGS.append(visitor_tgs)


	tgs_data = []
	#tgs_data.append(allTGS[0].Header())
	for tgs in allTGS:
		tgs_data.append(tgs.Compile_Stats())

	stats_to_compare = allTGS[0].Header()
	num_critical = 0
	num_warning = 0


	score = 0
	for offense in boxScore:
		stat_deltas,stat_diffs,num_warning_temp,num_critical_temp = compareGame(offense,tgs_data,stats_to_compare,False)
		score += GenAccuracyScore(stat_diffs)

		#num_critical += num_critical_temp
		#num_warning += num_warning_temp

	return score,tgs_data

#def ClassToDict()

def GenAccuracyScore(stat_diffs):
	score = 0
	if len(stat_diffs.keys()) == 0:
		print "PBP Was Not Found - returning score 0"
		return 0

	score += 180* (abs(stat_diffs['Pass TD']) + abs(stat_diffs['Rush TD'])  + abs(stat_diffs['Punt Ret TD'])  + abs(stat_diffs['Int Ret TD'])  + abs(stat_diffs['Kickoff Ret TD']) + abs(stat_diffs['Fum Ret TD'])+ abs(stat_diffs['Pass Int']) + abs(stat_diffs['Safety']))
	score += 1*(abs(stat_diffs['Pass Yard']) + abs(stat_diffs['Rush Yard'])  + abs(stat_diffs['Punt Ret Yard'])  + abs(stat_diffs['Int Ret Yard'])  + abs(stat_diffs['Kickoff Ret Yard']) + abs(stat_diffs['Fum Ret Yard']))
	score += 15*(abs(stat_diffs['Pass Att']) + abs(stat_diffs['Rush Att'])  + abs(stat_diffs['Pass Comp']))
	score += 45*(abs(stat_diffs['Field Goal Att']) + abs(stat_diffs['Field Goal Made'])  + abs(stat_diffs['Off XP Kick Att'])  + abs(stat_diffs['Off XP Kick Made'])  + abs(stat_diffs['Def 2XP Att']) + abs(stat_diffs['Def 2XP Made']))
	return score


def RecurPlayCombos(PlayComboList,CurGame,BestGame,BestScore,BestTGS,boxScore):

	if len(PlayComboList) < 1:
		Score,TGS = GameAccuracyScore(ConvertDictToGame(CurGame),boxScore)
		if Score < BestScore:
			BestGame = CurGame
			BestScore = Score
			BestTGS = TGS
		#print "Made it here"
		return BestGame,BestScore,BestTGS
	curPlay = PlayComboList.pop(0)
	for combo in curPlay:
		CurGame.append(combo)
		return RecurPlayCombos(PlayComboList,CurGame,BestGame,BestScore,BestTGS,boxScore)
		#CurGame.remove(combo)

	#return BestGame,BestScore

def MergePlayData(game1,game2,gameDict,boxScore):

	#catergories_to_check = ['Yards Gained','Off Touchdown','Def Touchdown','First Down','Completion','Interception',
	#					   'Fumble','Fumble Lost','Kick Good','TwoPt Good','Safety','Kick Yards',
	#					   'Kick Blocked','Penalty','No Play','Forced_Fum','Extra Pt Att','TwoPt Att']#,'Touchback','Kickoff OOB','Kickoff Onsides'

	catergories_to_check = ['Yards Gained','Off Touchdown','Def Touchdown','First Down','Completion','Interception',
						   'Fumble','Fumble Lost','Kick Good','TwoPt Good','Safety','Kick Yards',
						   'Kick Blocked','Penalty','No Play','Extra Pt Att','TwoPt Att','Play Type']#,'Touchback','Kickoff OOB','Kickoff Onsides' ,'Forced_Fum'
	playIndex = 0
	PlayComboList = []
	onlyTwo = False




	x = 0
	for play in gameDict:
		PlayCombos = []
		PlayCombos.append(play)
		if ('G1Index' in play and 'G2Index' in play) :
			G1Play = game1[int(play['G1Index'])]
			G2Play = game2[int(play['G2Index'])]


			for catergory in catergories_to_check:
				if str(G1Play[catergory]) != str(G2Play[catergory]):
					for index in range(len(PlayCombos)):
						play1=copy.deepcopy(PlayCombos.pop(0))
						play2 = copy.deepcopy(play1)
						play1[catergory] = G1Play[catergory]
						play2[catergory] = G2Play[catergory]

						PlayCombos.append(play1)
						PlayCombos.append(play2)
						if str(play[catergory]) != str(G2Play[catergory]) or str(play[catergory]) != str(G1Play[catergory]):
							play3 = copy.deepcopy(play1)
							play3[catergory] = play[catergory]
							PlayCombos.append(play3)
				elif str(play[catergory]) != str(G2Play[catergory]) or str(play[catergory]) != str(G1Play[catergory]):
					for index in range(len(PlayCombos)):
						play1=copy.deepcopy(PlayCombos.pop(0))
						play2 = copy.deepcopy(play1)
						play1[catergory] = G1Play[catergory]
						play2[catergory] = play[catergory]

						PlayCombos.append(play1)
						PlayCombos.append(play2)


		PlayComboList.append(PlayCombos)
		playIndex += 1

	BestCombo,BestScore,BestTGS =RecurPlayCombos(PlayComboList,[],[],99999,[],boxScore)
	return BestCombo,BestScore,BestTGS


def FindBestCombo(game1,game2,commonDict,diffDict,boxScore):

	best_accuracy =  999999
	best_data = 999999
	best_sequence = 999999
	best_modified = 999999
	bestTGS = []
	bestGame = None

	if len(diffDict) > 12:
		combo = 0
		for shift in range(len(diffDict)):
			combo0 =  combo
			binCombo0 =	bin(combo0)[2:].zfill(len(diffDict))

			combo1 = combo + 1 << shift
			binCombo1 =  bin(combo1)[2:].zfill(len(diffDict))

			gameDict0 = MakeGameFromCombo(binCombo0,commonDict,diffDict)
			gameCombo0 =  ConvertDictToGame(gameDict0)
			gameDict1 = MakeGameFromCombo(binCombo1,commonDict,diffDict)
			gameCombo1 =  ConvertDictToGame(gameDict1)

			outCombo0,num_bad_sequence0,num_bad_data0 = Bug_Check(gameCombo0,True)
			outCombo1,num_bad_sequence1,num_bad_data1 = Bug_Check(gameCombo1,True)

			if num_bad_sequence0 < num_bad_sequence1:
				combo = combo0
			elif num_bad_sequence1 < num_bad_sequence0:
				combo = combo1
			elif num_bad_data0 < num_bad_data1:
				combo = combo
			else:
				combo = combo1

		binCombo = bin(combo)[2:].zfill(len(diffDict))
		gameDict = MakeGameFromCombo(binCombo,commonDict,diffDict)
		gameCombo =  ConvertDictToGame(gameDict)

		outCombo,num_bad_sequence,num_bad_data = Bug_Check(gameCombo,True)
		outDict = ConvertGameToDict(outCombo)

		gameCombo,gameScore,TGS=MergePlayData(game1,game2,outDict,boxScore)
		if gameScore < best_accuracy:
			outCombo,num_bad_sequence,final_num_bad_data = Bug_Check(gameCombo,False)
			if final_num_bad_data < best_data:
				best_data = final_num_bad_data
				bestGame = gameCombo
				best_accuracy = gameScore
				bestTGS = TGS




	else:
		numCombos = int(math.pow(2,len(diffDict)))
		for combo in range(numCombos) :
			binCombo = bin(combo)[2:].zfill(len(diffDict))
			gameDict = MakeGameFromCombo(binCombo,commonDict,diffDict)
			gameCombo =  ConvertDictToGame(gameDict)

			## TODO This will currently not report a score, and will modify the data
			outCombo,num_bad_sequence,num_bad_data = Bug_Check(gameCombo,True)
			outDict = ConvertGameToDict(outCombo)
			#accuracyScore = GameAccuracyScore(game1,game2,commonDict,gameCombo,boxScore)
			#outCombo,after_num_bad_sequence,after_num_bad_data = Bug_Check(gameCombo,False)

			#sequences_modified = num_bad_sequence - after_num_bad_sequence
			#data_modified = num_bad_data - after_num_bad_data

			if num_bad_sequence <= best_sequence:
				best_sequence = num_bad_sequence
			if 1 == 1:
				gameCombo,gameScore,TGS=MergePlayData(game1,game2,outDict,boxScore)
				if gameScore < best_accuracy:
					outCombo,num_bad_sequence,final_num_bad_data = Bug_Check(gameCombo,False)
					if final_num_bad_data < best_data:
						best_data = final_num_bad_data
						bestGame = gameCombo
						best_accuracy = gameScore
						bestTGS = TGS


				#best_data = after_num_bad_sequence

	return bestGame,bestTGS

def MakeGameFromCombo(binCombo,commonDict,diffDict):
	outGame = copy.deepcopy(commonDict)
	offset = 0
	for diff in sorted(diffDict.iterkeys(),reverse = True, key=float):
		index = int(diff)
		binCombo,bit = binCombo[:-1],binCombo[-1]
		outGame[index:index] = diffDict[diff][bit]
	return outGame



def mergePlays(play1,play2,prev_play):
	#return play1

	#remove_play1,bad_drive_sequence1,bad_play_data1 =Check_Play(prev_play,play1,False)
	#remove_play2,bad_drive_sequence2,bad_play_data2 =Check_Play(prev_play,play2,False)

	catergories_to_check = ['Spot','Play Type','Yards Gained','Off Touchdown','Def Touchdown','First Down','Completion','Interception','Fumble','Fumble Lost','Kick Good','TwoPt Good','Safety','Kick Yards',
							'Touchback','Kickoff OOB','Kickoff Onsides','Kick Blocked','Penalty','Penalty Type','No Play','Rusher','Passer','Receiver','Kicker','Forced_Fum','Interceptor','Sacker','Extra Pt Att']

	outplay = play1
	catergories = play1.keys()

	#if prev_play == False:
	#	return outplay

	for catergory in catergories:
		if play1[catergory] != play2[catergory]:

			if play1[catergory] == '':
				outplay[catergory] = play2[catergory]
			elif play2[catergory] == '':
				outplay[catergory] = play1[catergory]

			## TODO THIS IS EXPERIMENTAL AND VERY GREEDY
			#if int(play1[catergory]) == 0 and abs(int(play2[catergory])) != 0 :
			#	outplay[catergory] = play2[catergory]
			#elif int(play2[catergory]) == 0 and abs(int(play1[catergory])) != 0 :
			#	outplay[catergory] = play1[catergory]

			#if catergory == 'Yards Gained':#catergory == 'Spot' or
			#	if not bad_play_data2:
			#		outplay[catergory] = play2[catergory]
			#	else:
			#		outplay[catergory] = play1[catergory]
			#if catergory == 'Play Desc':
			#	if play1['Play Type'] == 'Attempt':
			#		outplay[catergory] = play2[catergory]
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
	catergories_to_check = ['Offense Team Code','Down','Spot','Play Type','Distance','Completion']#,'Drive Number']
	retval = True


	#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because "

	if play1['Play Type'] == 'KICKOFF' and play2['Play Type'] == 'KICKOFF':
		if abs(int(play1['Kick Yards']) - int(play2['Kick Yards'])) < 2:
			return True
		#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Kickoff"
		return False
	elif play1['Play Type'] == 'FIELD GOAL' and play2['Play Type'] == 'FIELD GOAL':
		if abs(int(play1['Kick Yards']) - int(play2['Kick Yards'])) < 2:
			return True
		#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because FG"
		return False

	elif play1['Play Type'] == 'ATTEMPT' and play2['Play Type'] == 'ATTEMPT' and play1['Penalty'] == play2['Penalty'] and play1['No Play'] == play2['No Play']:
		return True

	#for catergory in catergories_to_check:
	#	if play1[catergory] != play2[catergory]:
	#		return False
	#return True





	Spot = True
	Distance = True
	Completion = True
	Penalty = True
	Down = True
	Offense = True
	Type = True
	if play1['Play Type'] != play2['Play Type']:
		Type = False
		#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Play Type"
	if play1['Spot'] != play2['Spot']:
		if abs(int(play1['Spot']) - int(play2['Spot'])) > 1:
			Spot = False
			#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Spot"
	if play1['Distance'] != play2['Distance']:
		if abs(int(play1['Distance']) - int(play2['Distance'])) > 1:
			Spot = False
			#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Distance"
	if play1['Play Type'] == 'PENALTY' or play2['Play Type'] == 'PENALTY':
		if int(play1['Penalty']) != int(play2['Penalty']):
			Penalty = False
			#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Penalty"
	if play1['Completion'] != play2['Completion']:
		if int(play1['Penalty']) != 1 or int(play2['Penalty']) != 1:
			Completion =  False
			#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Completion"
	if play1['Down'] != play2['Down']:
		#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Down"
		Down = False
	if play1['Offense Team Code'] != play2['Offense Team Code']:
		Offense = False
		#print play1['Play Desc'] + " Doesn't match "  + play2['Play Desc'] + " Because Offense"


	return Spot and Distance and Completion and Penalty and Down and Offense and Type


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
	diff1 = []
	diff2 = []
	for (key) in set(list(dict2.keys())) & set(list(dict1.keys())):
		common.append(key)
		print (key + " Matches Both!")
	for key in set(list(dict2.keys())):
		if key not in set(list(dict1.keys())):
			diff2.append(key)
	for key in set(list(dict1.keys())):
		if key not in set(list(dict2.keys())):
			diff1.append(key)
	common = sorted(common)
	diff1 = sorted(diff1)
	diff2 = sorted(diff2)
	return common,diff1,diff2




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

def main():
	path = "ESPN_Parser/" + str(year) + " Stats temp/"

	#CompESPN = ValidatePBP(path + 'play_TGS.csv',"2015 Stats/boxscore-stats.csv")
	headers = []
	outDrive = []
	with open(path + 'play.csv') as csv1:  #ESPN
		with open(path +'ncaa/play.csv') as csv2:  #CFB
			with open(str(year) + " Stats/boxscore-stats.csv") as boxcsv:
				with open(path + 'out_play_TGS.csv','w') as tgsout:
					boxScore = csv.reader(boxcsv)
					outDrive = compareDrives(csv1,csv2,boxScore,tgsout)#,CompESPN,CompNCAA)
		csv1.seek(0)
		reader = csv.DictReader(csv1)
		headers = reader.fieldnames

	with open(path + 'out_play.csv','w') as csvout:
		writer = csv.DictWriter(csvout,fieldnames=headers,extrasaction='ignore',lineterminator='\n')
		writer.writeheader()
		for line in outDrive:
			writer.writerow(line)


	ValidatePBP('ESPN_Parser/' + str(year) + ' Stats temp/out_play_TGS.csv',#ncaa/play_TGS.csv',
				str(year) +' Stats/boxscore-stats.csv')

	#writeCSV outplay.csv
	#OutReport = ValidatePBP('outplay.csv',outbox)

#main()