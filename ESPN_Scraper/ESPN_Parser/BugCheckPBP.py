__author__ = 'Ryan'

year = 2015

from Play_Stats import *
import csv


def Flag_Drive_Bad(game_code, drive_num, pbp_data):
	for play in pbp_data:
		if play.Game_Code == game_code and play.Drive_Number == drive_num:
			play.Bad_Drive = 1


def Check_Play(cur_play,next_play,modify_data):

	#try:
	cur_play = DictToPlay(cur_play)
	next_play = DictToPlay(next_play)
	#except:
	#	print "These aren't dicts, no need to convert"

	remove_play = False
	bad_drive_sequence = False
	bad_play_data = False


	anext_string = str(next_play.Down) + "&" + str(next_play.Distance) + " @ " + str(next_play.Spot) + "  :  " + next_play.Play_Desc
	############################
	#####  CRITICAL ERRORS #####
	############################

	if next_play.Play_Type == 'ATTEMPT':
		#cur_play.Extra_Pt_Att = next_play.Extra_Pt_Att
		#cur_play.TwoPt_Att = next_play.TwoPt_Att
		#cur_play.Kick_Good = next_play.Kick_Good
		#cur_play.TwoPt_Good = next_play.TwoPt_Good

		if next_play.Off_Points - cur_play.Off_Points == 1:
			if modify_data:
				cur_play.Extra_Pt_Att = 1
				cur_play.Kick_Good = 1
		elif next_play.Off_Points - cur_play.Off_Points == 2:
			if modify_data:
				cur_play.TwoPt_Att = 1
				cur_play.TwoPt_Good = 1
		if modify_data:
			cur_play.Off_Points = next_play.Off_Points

		if  cur_play.Def_Touchdown != 1 and cur_play.Off_Touchdown !=1:
			print " ATTEMPT WHEN PREV PLAY WASN'T A TOUCHDOWN"

		#pbp_data.remove(next_play)
		#remove_play = True
		#continue
		return remove_play,bad_drive_sequence,bad_play_data


	## Check out of order plays/ Down Sequence
	if int(next_play.Down) != int(cur_play.Down) + 1:
		if cur_play.Offense == next_play.Offense:
			if next_play.Down == 1:
				if cur_play.First_Down == 1:
					# This is fine
					pass
				else:
					if cur_play.Distance <= cur_play.Spot - next_play.Spot:
						print "This play should be a first down, and isn't labeled as such"
						bad_play_data = True
						if modify_data:
							cur_play.First_Down = 1
					else:
						if cur_play.Penalty == 1:
							# Its unclear if this is bad, this means we got a first down due to penalty, but didn't make distance. Auto 1st Down penalties are OK
							pass
						else:
							print "THIS IS BAD DOWN SEQUENCING"
							#Flag_Drive_Bad(cur_play.Game_Code, cur_play.Drive_Number, pbp_data)
							bad_drive_sequence = True
			else:
				if cur_play.No_Play:
					# this is OK, its  a replay down
					pass
				elif cur_play.Play_Type != 'KICKOFF' and next_play.Play_Type != 'KICKOFF':
					if cur_play.Penalty == 1 and cur_play.Down == next_play.Down:
						# probably missed a no play
						if modify_data:
							cur_play.No_Play = 1
							cur_play.Play_Type = 'PENALTY'
						bad_play_data = True
						print "Missed a no play on this penalty!"
					else:
						print "THIS IS BAD DOWN SEQUENCING"
						#Flag_Drive_Bad(cur_play.Game_Code, cur_play.Drive_Number, pbp_data)
						bad_drive_sequence = True

	if int(next_play.Down) != 4 and next_play.Play_Type == 'PUNT':
		print "Who punts before 4th!?"
		if int(cur_play.Down) == 3:
			print "They Didn't actually get that first down..."
			if modify_data:
				cur_play.First_Down = 0
				next_play.Down = 4
			bad_play_data = True

	#if (int(cur_play.Distance) - int(next_play.Distance)) * (int(cur_play.Spot) - int(next_play.Spot)) < 0 and (cur_play.Play_Type == 'RUN' or cur_play.Play_Type == 'PASS') :
	if (int(cur_play.Yards_Gained)) * (int(cur_play.Spot) - int(next_play.Spot)) < 0 and cur_play.Penalty != 1 and (cur_play.Play_Type == 'RUN' or cur_play.Play_Type == 'PASS')and (cur_play.Offense == next_play.Offense) :

		print "Going backwards on the field, Should never happen"
		if modify_data:
			cur_play.Spot = 100 - int(cur_play.Spot)
		bad_play_data = True

	############################
	#####  INTEGRITY ERRORS ####
	############################

	if cur_play.No_Play == 1 and (cur_play.Down < next_play.Down and cur_play.First_Down == 0):
		# Probably not a no play
		print "NOT a no play"
		if modify_data:
			cur_play.No_Play = 0
		bad_play_data = True

	if cur_play.Fumble:
		if cur_play.Offense == next_play.Defense or cur_play.Def_Touchdown == 1 and cur_play.Off_Touchdown != 1:
			if cur_play.Fumble_Lost == 0:
				print "Missed Fumble Lost"
				if modify_data:
					cur_play.Fumble_Lost = 1
				#bad_play_data = True

	if abs(int(cur_play.Yards_Gained) - (int(cur_play.Spot) - int(next_play.Spot))) > 1:
		if cur_play.Fumble != 1 and cur_play.Interception != 1 and (cur_play.Play_Type == 'RUN' or cur_play.Play_Type == 'PASS') and cur_play.Penalty == 0 and (cur_play.Offense == next_play.Offense):
			print "Yards Gained > 2 off"
			## Not sure how to handle
			if modify_data:
				print "DOING NOTHING NOW"
				#cur_play.Yards_Gained = int(cur_play.Spot) - int(next_play.Spot)
			bad_play_data = True

	return remove_play,bad_drive_sequence,bad_play_data


def Bug_Check(pbp_data):
	#prev_play = Play_Stats(0, 0, 0, 0, 0, 0, 0, 0, 0)
	cur_play = Play_Stats(0, 0, 0, 0, 0, 0, 0, 0, 0)
	for next_play in pbp_data:

		remove_play,bad_drive_sequence,bad_play_data = Check_Play(cur_play,next_play,True)
		if bad_drive_sequence:
			Flag_Drive_Bad(cur_play.Game_Code, cur_play.Drive_Number, pbp_data)







		## Set Items for next cycle
		prev_play = cur_play
		cur_play = next_play
		acur_string = str(next_play.Down) + "&" + str(next_play.Distance) + " @ " + str(next_play.Spot) + "  :  " + next_play.Play_Desc
	return pbp_data

def DictToPlay(play):
	newplay = Play_Stats(0, 0, 0, 0, 0, 0, 0, 0, 0)
	if play == False:
		return newplay
	newplay.Game_Code =play['Game Code']
	newplay.Play_Number=int(play['Play Number'])
	newplay.Period_Number =int(play['Period Number'])
	newplay.Drive_Start =play['Drive Start']
	newplay.Offense =play['Offense Team Code']
	newplay.Defense =play['Defense Team Code']
	newplay.Off_Points =int(play['Offense Points'])
	newplay.Def_Points =int(play['Defense Points'])
	newplay.Down =int(play['Down'])  if play['Down'] != '' else 0
	newplay.Distance =int(play['Distance'])  if play['Distance'] != '' else 0
	newplay.Spot =int(play['Spot']) if play['Spot'] != '' else 0
	newplay.Play_Type =play['Play Type']
	newplay.Drive_Number =int(play['Drive Number']) if play['Drive Number'] != '' else 0
	newplay.Drive_Play =int(play['Drive Play']) if play['Drive Play'] != '' else 0
	newplay.Play_Desc =play['Play Desc']
	newplay.Play_Result =play['Play Result']
	newplay.Yards_Gained =int(play['Yards Gained'])
	newplay.Off_Touchdown =int(play['Off Touchdown'])
	newplay.Def_Touchdown =int(play['Def Touchdown'])
	newplay.First_Down =int(play['First Down'])
	newplay.Completion =int(play['Completion'])
	newplay.Interception =int(play['Interception'])
	newplay.Fumble =int(play['Fumble'])
	newplay.Fumble_Lost =int(play['Fumble Lost'])
	newplay.Kick_Good =int(play['Kick Good'])
	newplay.TwoPt_Good =int(play['TwoPt Good'])
	newplay.Safety =int(play['Safety'])
	newplay.Kick_Yards =int(play['Kick Yards'])
	newplay.Touchback =int(play['Touchback'])
	newplay.Kickoff_OOB =int(play['Kickoff OOB'])
	newplay.Kickoff_Onsides =int(play['Kickoff Onsides'])
	newplay.Kick_Blocked =int(play['Kick Blocked'])
	newplay.Penalty =int(play['Penalty'])
	newplay.Penalty_Type =play['Penalty Type']
	newplay.No_Play =int(play['No Play'])
	newplay.Rusher =play['Rusher']
	newplay.Passer =play['Passer']
	newplay.Receiver =play['Receiver']
	newplay.Kicker =play['Kicker']
	newplay.Forced_Fum =play['Forced_Fum']
	newplay.Interceptor =play['Interceptor']
	newplay.Sacker =play['Sacker']
	newplay.Extra_Pt_Att =int(play['Extra Pt Att'])
	newplay.TwoPt_Att =int(play['TwoPt Att'])
	newplay.Unparsed =play['Unparsed Play Desc']
	return newplay

def CsvToPlays(path):

	outPlays = []

	with open (path) as csv1:
		reader = csv.DictReader(csv1)

		for play in reader:
			newplay = DictToPlay(play)

			outPlays.append(newplay)
	return outPlays

# Writes the contents of data to a .csv file
def Write_CSV(data, file_name):
	with open(file_name, "w") as csvfile:
		data_writer = csv.writer(csvfile, lineterminator = '\n')
		data_writer.writerows(data)



##########
## MAIN ##
##########

#pbpfile = 'play.csv'
#path =  str(year) + ' Stats temp/'
#pbpData = CsvToPlays(path + pbpfile)
#outPbp = Bug_Check(pbpData)
'''
print "ROUND TWO"

outPbp = Bug_Check(outPbp)

print "ROUND THREE"

outPbp = Bug_Check(outPbp)
print "ROUND Four"

outPbp = Bug_Check(outPbp)
print "ROUND Five"

outPbp = Bug_Check(outPbp)
'''
#play_data = []
#play_data.append(outPbp[0].Header())
#for play in outPbp:
#	play_data.append(play.Compile_Stats())
#Write_CSV(play_data, path+'play_modified.csv')