
import csv
import os

year = 2015

##
#
#  KNOWN ISSUES THAT ARE NOT PROBLEMS
#   IF A TEAM SCORES THEIR LAST POINTS ON A RETURN OR ON DEFENSE, SCORE WILL BE WRONG
#   ESPN ISN'T ALWAYS CORRECT WHEN THEY COUNT A PLAY, SOMETIMES NO PLAYS ARE COUNTED TO RUSH OR PASS TOTALS
#   espn.go.com/college-football/boxscore?gameId=400763589, PRIME EXAMPLE OF A BUGGED ESPN
#   FUMBLE AND INTERCEPTION YARDS AREN'T ADDED, OR COMPUTED TO THAT DEGREE, SO WE ARE OFF SOME ON THOSE
#
#

def Read_CSV(file_name):
	data = []
	with open(file_name, "rU") as csvfile:
		data_reader = csv.reader(csvfile)
		for row in data_reader:
			data.append(row)

	#data.pop(0)
	return data

def FindGame(game_id):


	#basePath = '../rcfbScraper/ESPN_Scraper/'
	basePath = str(year)
	filename = str(game_id)
	while len(filename) != 16:
		filename = "0"+filename

	for x in range (1,18):
		path = basePath+"/scraped_games/week_"+str(x)+"/"+filename+".txt"
		if os.path.isfile(path):
			break

	file = open(path,'r')
	file.readline()
	homeString = file.readline()
	homeString = homeString[6:]
	home = homeString.split("(",1)[0][:-1]
	homeCode = homeString.split("(",2)[-1][:-2]
	visitorString=file.readline()
	visitorString = visitorString[6:]
	visitor = visitorString.split("(",2)[0][:-1]
	visitorCode = visitorString.split("(",2)[-1][:-2]
	playsString = file.readline()
	plays = playsString[9:-1]
	drives = file.readline()
	box = file.readline();
	return home,homeCode,visitor,visitorCode,plays

def compareGame(box_game,pbp_arr,stats_to_lookup):

	stat_deltas = []
	stat_diffs = []
	num_warning = 0
	num_critical = 0
	stat_report = [0] * len(stats_to_lookup)

	for x in range(0, len(stats_to_lookup)):
		empty_arr1 = []
		#empty_arr2 = []
		stat_deltas.append(empty_arr1)
		stat_diffs.append(0)

	match = []
	home,homeCode,visitor,visitorCode,pbp = FindGame(box_game[1])
	offense = ''
	if int(homeCode) == int(box_game[0]):
		offense = home
	else:
		offense = visitor
	for pbp_line in pbp_arr:
		if float(pbp_line[0]) == float(box_game[0]) and float(pbp_line[1]) == float(box_game[1]):
			match = pbp_line
	if not match:

		print "No PBP match found for " + home + " vs " + visitor +" " + pbp + " " + box_game[1]

		return stat_deltas,stat_diffs,0,0

	skipnames = ["Time Of Possession","Fourth Down Conv","Fourth Down Att", "Third Down Att","Third Down Conv","Kickoff Ret","Punt Ret","Kickoff","Fumble",
					 "Fumble Lost","1st Down Rush","1st Down Pass","Kickoff Yard","Off 2XP Att","Off 2XP Made"]
	skiplist = []
	for stat in skipnames:
		skiplist.append(stats_to_lookup.index(stat))

	print "Comparing Data as " + offense + " in " + visitor + " @ " + home +" " + pbp + " " + box_game[1]
	for x in range(0, len(stats_to_lookup)):

		diff = float(match[x]) - float(box_game[x])
		stat_diffs[x] = diff
		if x in skiplist:
			continue;

		aval1 = float(box_game[x])
		aval2 = float(match[x])

		if float(box_game[x]) == 0:# or float(match[x]) == 0:
			#continue
			delta = abs((float(match[x]) - float(box_game[x])) / 1)
		else:
			delta = abs((float(match[x]) - float(box_game[x])) / float(box_game[x]))


		stat_deltas[x].append(delta)

		if delta > 0.5:
			print "    CRITICAL: Huge difference at " + stats_to_lookup[x] + " pbp:" + match[x] + " vs box:" + box_game[x]
			num_critical += 1
		elif delta > 0:
			print "    Warning: Small difference at " + stats_to_lookup[x] + " pbp:" + match[x] + " vs box:" + box_game[x]
			num_warning += 1
	return stat_deltas,stat_diffs,num_warning,num_critical






def ValidatePBP(PBPCSV, BoxCSV):



	pbp_arr = Read_CSV(PBPCSV)
	box_arr = Read_CSV(BoxCSV)

	stats_to_lookup = pbp_arr.pop(0)
	box_arr.pop(0)


	stat_deltas = []
	stat_report = [0] * len(stats_to_lookup)

	for x in range(0, len(stats_to_lookup)):
		empty_arr = []
		stat_deltas.append(empty_arr)

	num_critical = 0
	num_warning = 0

	outDict = {}

	for line in box_arr:

		stat_deltas_new,stat_diff,num_warning_new,num_critical_new = compareGame(line,pbp_arr,stats_to_lookup)
		num_critical += num_critical_new
		num_warning += num_warning_new
		for x in range(len(stat_deltas)):
			stat_deltas[x] += stat_deltas_new[x]

		key = line[0] + '-' + line[1]
		#outDict['poop'] = stat_diff
		outDict[key] = stat_diff




	num_errors = [0] * len(stats_to_lookup)
	for x in range(0, len(stat_deltas)):
		delta = stat_deltas[x]
		if not delta:
			continue
		stat_report[x] =  100 * sum(delta) / len(delta)
		for i in delta:
			if i != 0:
				num_errors[x] += 1



	for x in range(0, len(stat_report)):
		if num_errors[x] == 0 and len(stat_deltas[x]) - num_errors[x] ==0:
			continue
		print stats_to_lookup[x] + " is off by Average of: " + str(int(stat_report[x])) +  "% with " + str(num_errors[x]) + " errors and " + str(len(stat_deltas[x]) - num_errors[x]) + " exactly correct"

	print "Number of CRITICAL stats (over 100% off) is " + str(num_critical)
	print "Number of incorrect stats (<100% & >20% off) is " + str(num_warning)

	return outDict

######################
##### MAIN ##########
####################


#ValidatePBP('../rcfbScraper/ESPN_Scraper/2014 Stats/play_TGS.csv',
#			'../rcfbScraper/ESPN_Scraper/2014 Stats/team-game-statistics.csv')
ValidatePBP('ESPN_Parser/' + str(year) + ' Stats temp/ncaa/play_TGS.csv',
			str(year) +' Stats/boxscore-stats.csv')