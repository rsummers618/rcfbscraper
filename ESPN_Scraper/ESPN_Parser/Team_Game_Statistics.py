import re
from Play_Stats import *

# Holds the data for a team-game stats
class Team_Game_Statistics:

	# Constructor
	def __init__(self, game_code, team_code):
		self.Game_Code = game_code
		self.Team_Code = team_code
		self.Rush_Att = 0
		self.Rush_Yard = 0
		self.Rush_TD = 0
		self.Pass_Att = 0
		self.Pass_Comp = 0
		self.Pass_Yard = 0
		self.Pass_TD = 0
		self.Pass_Int = 0

		# NOT DONE START --------------------
		self.Pass_Conv = 0  # still have no idea what this is
		self.Kickoff_Ret = 0
		self.Kickoff_Ret_Yard = 0
		self.Kickoff_Ret_TD = 0
		self.Punt_Ret = 0
		self.Punt_Ret_Yard = 0
		self.Punt_Ret_TD = 0
		self.Fum_Ret = 0
		self.Fum_Ret_Yard = 0
		self.Fum_Ret_TD = 0
		self.Int_Ret = 0
		self.Int_Ret_Yard = 0
		self.Int_Ret_TD = 0
		self.Misc_Ret = 0
		self.Misc_Ret_Yard = 0
		self.Misc_Ret_TD = 0
		self.Field_Goal_Att = 0
		self.Field_Goal_Made = 0
		self.Off_XP_Kick_Att = 0
		self.Off_XP_Kick_Made = 0
		self.Off_2XP_Att = 0
		self.Off_2XP_Made = 0
		self.Def_2XP_Att = 0
		self.Def_2XP_Made = 0
		self.Safety = 0
		# NOT DONE END ----------------------

		self.Points = 0

		# NOT DONE START --------------------
		self.Punt = 0
		self.Punt_Yard = 0
		self.Kickoff = 0
		self.Kickoff_Yard = 0
		self.Kickoff_Touchback = 0
		self.Kickoff_Out_Of_Bounds = 0
		self.Kickoff_Onsides = 0
		# NOT DONE END ----------------------

		self.Fumble = 0
		self.Fum_Lost = 0

		# NOT DONE START --------------------
		self.Tackle_Solo = 0
		self.Tackle_Assist = 0
		self.Tackle_For_Loss = 0
		self.Tackle_For_Loss_Yard = 0
		self.Sack = 0
		self.Sack_Yard = 0
		self.QB_Hurry = 0
		self.Fum_Forced = 0
		self.Pass_Broken_Up = 0
		self.Kick_Punt_Blocked = 0
		# NOT DONE END ----------------------

		self.First_Down_Rush = 0
		self.First_Down_Pass = 0

		# NOT DONE START --------------------
		self.First_Down_Penalty = 0
		self.Time_Of_Possession = 0
		self.Penalty = 0
		self.Penalty_Yard = 0
		# NOT DONE END ----------------------

		self.Third_Down_Att = 0
		self.Third_Down_Conv = 0
		self.Fourth_Down_Att = 0
		self.Fourth_Down_Conv = 0

		# NOT DONE START --------------------
		self.Red_Zone_Att = 0
		self.Red_Zone_TD = 0
		self.Red_Zone_Field_Goal = 0
		# NOT DONE END ----------------------


	# Adds a play's stats to the overall game stats
	def Extract_Play_Offense(self, play,defense_tgs):

		# Get play type sensitive data
		if play.No_Play == 0:
			if play.Play_Type == "RUSH":
				self.Rush_Att += 1
				self.Rush_Yard += play.Yards_Gained
				self.Rush_TD += play.Off_Touchdown
				self.First_Down_Rush += play.First_Down
			elif play.Play_Type == "PASS":
				self.Pass_Att += 1
				self.Pass_Comp += play.Completion
				if play.Interception != 1:
					self.Pass_Yard += play.Yards_Gained
				else:
					defense_tgs.Int_Ret_Yard += play.Yards_Gained
					defense_tgs.Int_Ret += 1
					defense_tgs.Int_Ret_TD += play.Def_Touchdown
				self.Pass_TD += play.Off_Touchdown
				self.Pass_Int += play.Interception
				self.First_Down_Pass += play.First_Down
			elif play.Play_Type == "SACK":
				self.Rush_Att += 1
				self.Rush_Yard += play.Yards_Gained
			elif play.Play_Type == "KICKOFF":
				self.Kickoff += 1
				self.Kickoff_Yard += int(play.Kick_Yards)
				self.Kickoff_Ret_Yard += play.Yards_Gained
				self.Kickoff_Ret_TD += play.Off_Touchdown
			elif play.Play_Type == "PUNT":
				self.Punt += 1
				self.Punt_Yard += play.Kick_Yards
				defense_tgs.Punt_Ret_Yard+= play.Yards_Gained
				defense_tgs.Punt_Ret_TD += play.Def_Touchdown
			elif play.Play_Type == "FIELD GOAL":
				self.Field_Goal_Att +=1
				self.Field_Goal_Made +=play.Kick_Good


		# Down sensitive data
		if int(play.Down) == 3:
			self.Third_Down_Att += 1
			self.Third_Down_Conv += play.First_Down or play.Off_Touchdown
		elif int(play.Down) == 4:
			self.Fourth_Down_Att += 1
			self.Fourth_Down_Conv += play.First_Down or play.Off_Touchdown

		# Misc data
		self.Points = play.Off_Points
		defense_tgs.Points = play.Def_Points
		self.Fumble += play.Fumble
		self.Fum_Lost += play.Fumble_Lost
		if play.Off_Touchdown:
			self.Off_2XP_Att += play.TwoPt_Att
			self.Off_2XP_Made += play.TwoPt_Good
			self.Off_XP_Kick_Att += play.Extra_Pt_Att
			if play.Extra_Pt_Att:
				self.Off_XP_Kick_Made += play.Kick_Good
		if play.Def_Touchdown:
			defense_tgs.Off_2XP_Att += play.TwoPt_Att
			defense_tgs.Off_2XP_Made += play.TwoPt_Good
			defense_tgs.Off_XP_Kick_Att += play.Extra_Pt_Att
			if play.Extra_Pt_Att:
				defense_tgs.Off_XP_Kick_Att += play.Kick_Good


	# Returns an array of relavent information
	def Compile_Stats(self):
		OutputArray = []
		OutputArray.append(str(self.Team_Code))
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Rush_Att))
		OutputArray.append(str(self.Rush_Yard))
		OutputArray.append(str(self.Rush_TD))
		OutputArray.append(str(self.Pass_Att))
		OutputArray.append(str(self.Pass_Comp))
		OutputArray.append(str(self.Pass_Yard))
		OutputArray.append(str(self.Pass_TD))
		OutputArray.append(str(self.Pass_Int))
		OutputArray.append(str(self.Pass_Conv))
		OutputArray.append(str(self.Kickoff_Ret))
		OutputArray.append(str(self.Kickoff_Ret_Yard))
		OutputArray.append(str(self.Kickoff_Ret_TD))
		OutputArray.append(str(self.Punt_Ret))
		OutputArray.append(str(self.Punt_Ret_Yard))
		OutputArray.append(str(self.Punt_Ret_TD))
		OutputArray.append(str(self.Fum_Ret))
		OutputArray.append(str(self.Fum_Ret_Yard))
		OutputArray.append(str(self.Fum_Ret_TD))
		OutputArray.append(str(self.Int_Ret))
		OutputArray.append(str(self.Int_Ret_Yard))
		OutputArray.append(str(self.Int_Ret_TD))
		OutputArray.append(str(self.Misc_Ret))
		OutputArray.append(str(self.Misc_Ret_Yard))
		OutputArray.append(str(self.Misc_Ret_TD))
		OutputArray.append(str(self.Field_Goal_Att))
		OutputArray.append(str(self.Field_Goal_Made))
		OutputArray.append(str(self.Off_XP_Kick_Att))
		OutputArray.append(str(self.Off_XP_Kick_Made))
		OutputArray.append(str(self.Off_2XP_Att))
		OutputArray.append(str(self.Off_2XP_Made))
		OutputArray.append(str(self.Def_2XP_Att))
		OutputArray.append(str(self.Def_2XP_Made))
		OutputArray.append(str(self.Safety))
		OutputArray.append(str(self.Points))
		OutputArray.append(str(self.Punt))
		OutputArray.append(str(self.Punt_Yard))
		OutputArray.append(str(self.Kickoff))
		OutputArray.append(str(self.Kickoff_Yard))
		OutputArray.append(str(self.Kickoff_Touchback))
		OutputArray.append(str(self.Kickoff_Out_Of_Bounds))
		OutputArray.append(str(self.Kickoff_Onsides))
		OutputArray.append(str(self.Fumble))
		OutputArray.append(str(self.Fum_Lost))
		OutputArray.append(str(self.Tackle_Solo))
		OutputArray.append(str(self.Tackle_Assist))
		OutputArray.append(str(self.Tackle_For_Loss))
		OutputArray.append(str(self.Tackle_For_Loss_Yard))
		OutputArray.append(str(self.Sack))
		OutputArray.append(str(self.Sack_Yard))
		OutputArray.append(str(self.QB_Hurry))
		OutputArray.append(str(self.Fum_Forced))
		OutputArray.append(str(self.Pass_Broken_Up))
		OutputArray.append(str(self.Kick_Punt_Blocked))
		OutputArray.append(str(self.First_Down_Rush))
		OutputArray.append(str(self.First_Down_Pass))
		OutputArray.append(str(self.First_Down_Penalty))
		OutputArray.append(str(self.Time_Of_Possession))
		OutputArray.append(str(self.Penalty))
		OutputArray.append(str(self.Penalty_Yard))
		OutputArray.append(str(self.Third_Down_Att))
		OutputArray.append(str(self.Third_Down_Conv))
		OutputArray.append(str(self.Fourth_Down_Att))
		OutputArray.append(str(self.Fourth_Down_Conv))
		OutputArray.append(str(self.Red_Zone_Att))
		OutputArray.append(str(self.Red_Zone_Field_Goal))
		OutputArray.append(str(self.Red_Zone_TD))
		return OutputArray


	# Returns the header for a play type
	def Header(self):
		OutputArray = []
		OutputArray.append("Team Code")
		OutputArray.append("Game Code")
		OutputArray.append("Rush Att")
		OutputArray.append("Rush Yard")
		OutputArray.append("Rush TD")
		OutputArray.append("Pass Att")
		OutputArray.append("Pass Comp")
		OutputArray.append("Pass Yard")
		OutputArray.append("Pass TD")
		OutputArray.append("Pass Int")
		OutputArray.append("Pass Conv")
		OutputArray.append("Kickoff Ret")
		OutputArray.append("Kickoff Ret Yard")
		OutputArray.append("Kickoff Ret TD")
		OutputArray.append("Punt Ret")
		OutputArray.append("Punt Ret Yard")
		OutputArray.append("Punt Ret TD")
		OutputArray.append("Fum Ret")
		OutputArray.append("Fum Ret Yard")
		OutputArray.append("Fum Ret TD")
		OutputArray.append("Int Ret")
		OutputArray.append("Int Ret Yard")
		OutputArray.append("Int Ret TD")
		OutputArray.append("Misc Ret")
		OutputArray.append("Misc Ret Yard")
		OutputArray.append("Misc Ret TD")
		OutputArray.append("Field Goal Att")
		OutputArray.append("Field Goal Made")
		OutputArray.append("Off XP Kick Att")
		OutputArray.append("Off XP Kick Made")
		OutputArray.append("Off 2XP Att")
		OutputArray.append("Off 2XP Made")
		OutputArray.append("Def 2XP Att")
		OutputArray.append("Def 2XP Made")
		OutputArray.append("Safety")
		OutputArray.append("Points")
		OutputArray.append("Punt")
		OutputArray.append("Punt Yard")
		OutputArray.append("Kickoff")
		OutputArray.append("Kickoff Yard")
		OutputArray.append("Kickoff Touchback")
		OutputArray.append("Kickoff Out-Of-Bounds")
		OutputArray.append("Kickoff Onside")
		OutputArray.append("Fumble")
		OutputArray.append("Fumble Lost")
		OutputArray.append("Tackle Solo")
		OutputArray.append("Tackle Assist")
		OutputArray.append("Tackle For Loss")
		OutputArray.append("Tackle For Loss Yard")
		OutputArray.append("Sack")
		OutputArray.append("Sack Yard")
		OutputArray.append("QB Hurry")
		OutputArray.append("Fumble Forced")
		OutputArray.append("Pass Broken Up")
		OutputArray.append("Kick/Punt Blocked")
		OutputArray.append("1st Down Rush")
		OutputArray.append("1st Down Pass")
		OutputArray.append("1st Down Penalty")
		OutputArray.append("Time Of Possession")
		OutputArray.append("Penalty")
		OutputArray.append("Penalty Yard")
		OutputArray.append("Third Down Att")
		OutputArray.append("Third Down Conv")
		OutputArray.append("Fourth Down Att")
		OutputArray.append("Fourth Down Conv")
		OutputArray.append("Red Zone Att")
		OutputArray.append("Red Zone TD")
		OutputArray.append("Red Zone Field Goal")
		return OutputArray
