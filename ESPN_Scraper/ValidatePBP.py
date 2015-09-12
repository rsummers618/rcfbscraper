
import csv
import os

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
	basePath = '2014'
	filename = str(game_id)
	while len(filename) != 16:
		filename = "0"+filename

	for x in range (1,18):
		path = basePath+"/week_"+str(x)+"/"+filename+".txt"
		if os.path.isfile(path):
			break

	file = open(path,'r')
	file.readline()
	homeString = file.readline()
	homeString = homeString[6:]
	home = homeString.split("(",1)[0][:-1]
	homeCode = homeString.split("(",2)[-1][:-2]
	visitorString=file.readline()
	visitorString = visitorString[9:]
	visitor = visitorString.split("(",2)[0][:-1]
	visitorCode = visitorString.split("(",2)[-1][:-2]
	playsString = file.readline()
	plays = playsString[9:-1]
	drives = file.readline()
	box = file.readline();
	return home,homeCode,visitor,visitorCode,plays

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

	for line in box_arr:
		match = []
		home,homeCode,visitor,visitorCode,pbp = FindGame(line[1])
		offense = ''
		if int(homeCode) == int(line[0]):
			offense = home
		else:
			offense = visitor
		for pbp_line in pbp_arr:
			if float(pbp_line[0]) == float(line[0]) and float(pbp_line[1]) == float(line[1]):
				match = pbp_line
		if not match:

			print "No PBP match found for " + home + " vs " + visitor +" " + pbp + " " + line[1]

			continue


		print "Comparing Data as " + offense + " in " + visitor + " @ " + home +" " + pbp + " " + line[1]
		for x in range(0, len(stats_to_lookup)):
			skiplist = stats_to_lookup.index("Time Of Possession")
			if x == skiplist:
				continue;
			if float(line[x]) == 0 or float(match[x]) == 0:
				continue
			delta = abs((float(match[x]) - float(line[x])) / float(line[x]))

			stat_deltas[x].append(delta)
			if delta > 1:
				print "    CRITICAL: Huge difference at " + stats_to_lookup[x] + " pbp:" + match[x] + " vs box:" + line[x]
				num_critical += 1
			elif delta > 0.2:
				print "    Warning: Small difference at " + stats_to_lookup[x] + " pbp:" + match[x] + " vs box:" + line[x]
				num_warning += 1

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

######################
##### MAIN ##########
####################


#ValidatePBP('../rcfbScraper/ESPN_Scraper/2014 Stats/play_TGS.csv',
#			'../rcfbScraper/ESPN_Scraper/2014 Stats/team-game-statistics.csv')
ValidatePBP('2014 Stats/play_TGS.csv',
			'2014 Stats/team-game-statistics.csv')