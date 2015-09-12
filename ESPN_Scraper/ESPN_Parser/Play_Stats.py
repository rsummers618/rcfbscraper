import re

# Holds the data for a team-game stats
class Play_Stats:

	# Constructor
	def __init__(self, game_code, play_num, period, drv_start, Off, Def, off_pnts, def_pnts, drv_num):
		self.Game_Code = game_code
		self.Play_Number = play_num
		self.Period_Number = period
		self.Drive_Start = drv_start
		self.Offense = Off
		self.Defense = Def
		self.Off_Points = off_pnts
		self.Def_Points = def_pnts
		self.Down = 0
		self.Distance = 0
		self.Spot = 0
		self.Play_Type = ""
		self.Drive_Number = drv_num
		self.Drive_Play = 0
		self.Play_Desc = ""
		self.Play_Result = ""
		self.Yards_Gained = 0
		self.Off_Touchdown = 0
		self.Def_Touchdown = 0
		self.First_Down = 0
		self.Completion = 0
		self.Interception = 0
		self.Fumble = 0
		self.Fumble_Lost = 0
		self.Kick_Good = 0
		self.TwoPt_Good = 0
		self.Safety = 0
		self.Kick_Yards = 0
		self.Touchback = 0
		self.Kickoff_OOB = 0
		self.Kickoff_Onsides = 0
		self.Kick_Blocked = 0
		self.Penalty = 0
		self.Penalty_Type = 0
		self.No_Play = 0
		self.Rusher = ""
		self.Passer = ""
		self.Receiver = ""
		self.Kicker = ""
		self.Forced_Fum = ""
		self.Interceptor = ""
		self.Sacker = ""
		self.Extra_Pt_Att = 0
		self.TwoPt_Att = 0
		self.Unparsed = ""


	# Extracts play data from play-by-play
	def Extract_Play_Data(self, play, prev_play):
		if len(play) < 2:
			return False
		play_info = play[0]
		play_desc = play[1]
		self.Play_Desc = play_desc

		# Get down and distance
		self.Get_Play_Info(play_info)

		# Define regex types
		rush1 = re.match(r"((?P<rusher>\D+) (?:run|rush).*for\s*)", play_desc)
		rush2 = re.match(r"((?P<rusher>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:run|rush)\s*)", play_desc,re.IGNORECASE)
		sack = re.match(r"((?P<passer>\D+) sacked by )", play_desc)
		pass_cmp = re.match(r"((?P<passer>\D+) pass complete\s*)", play_desc)
		pass_inc = re.match(r"((?P<passer>\D+) pass incomplete\s*)", play_desc)
		pass_int = re.match(r"((?P<passer>\D+) pass intercepted\s*)", play_desc)
		pass_td = re.match(r"((?P<receiver>\D+)(?P<yards>\d+) (?:yd|yard|yds|yards) pass from (?P<passer>\D+)\s*)", play_desc,re.IGNORECASE)
		loss_regex = re.compile(r"(a loss of\s*)")
		yard_regex = re.compile(r"(((?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain)\W+)")
		postn_regex = re.compile(r"(to the t(?P<field_half>\d+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to the (?P<fifty>50) (?:yard|yd) line(?:,)?\s*)")
		first_regex = re.compile(r"(for a (?P<fd>1ST down))", re.IGNORECASE)
		safe_regex = re.compile(r"(for a (?P<safety>SAFETY)\s*)")
		fumb_regex = re.compile(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)")
		frcd_regex = re.compile(r"(forced by (?P<forcer>\D+),\s)")
		flost_regex = re.compile(r"(recovered by t(?P<team>\d+)(?: (?P<player>[^,]+))?(?:\W\s)?)")
		fret_regex = re.compile(r"(return for (?P<yards>\d+) (?:yards|yard|yds|yd)\s*)")
		td_regex = re.compile(r"(for a (?P<td>TD|TOUCHDOWN))", re.IGNORECASE)
		expt_regex1 = re.compile(r"((?:, )?(?: )?\((?P<kicker>\D+) KICK\))", re.IGNORECASE)
		rcvr1_regex = re.compile(r"(to (?P<receiver>\D+)\Z)")
		rcvr2_regex = re.compile(r"(to (?P<receiver>\D+) for\W+)")
		rcvr3_regex = re.compile(r"(to (?P<receiver>\D+))")
		int_regex = re.compile(r"((?P<interceptor>\D+) return )")
		sacker_regex = re.compile(r"((?:(?P<sacker>\D+)|(?P<sacker_group>\D+ and \D+)) for )")
		punt = re.match(r"((?P<punter>\D+) (?:punt|punts) for\s*)", play_desc,re.IGNORECASE)
		punt_blocked = re.match(r"((?P<punter>\D+) (?:punt|punts) blocked\s*)", play_desc,re.IGNORECASE)
		kickoff = re.match(r"((?P<kicker>\D+) (?:kickoff) for\s*)", play_desc,re.IGNORECASE)
		kick_return = re.compile(r"((?P<returner>\D+) (?:return|returns) for\s*)",re.IGNORECASE)
		fg1 = re.match(r"((?P<kicker>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:FG|field goal)\s*)", play_desc,re.IGNORECASE)
		fg2 = re.match(r"(FG|field goal)", play_desc,re.IGNORECASE)
		fg_good_regex = re.compile(r"(GOOD|MADE\s*)",re.IGNORECASE)
		penalty = re.match(r"((?P<team>.*)(?: Penalty|Penalty,| Penalty,|Penalty)(?P<penalty>.*)\((?P<yds>.*)\)\s*)", play_desc,re.IGNORECASE)
		penalty_no_play = re.match(r"(.*(?:Penalty)*NO PLAY*)", play_desc,re.IGNORECASE)
		fumble_return =re.match(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:turnover|fumble) Return\s*)", play_desc,re.IGNORECASE)
		kickoff_return =re.match(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:kick|kickoff) Return\s*)", play_desc,re.IGNORECASE)
		punt_return =re.match(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:punt) Return\s*)", play_desc,re.IGNORECASE)
		int_return =re.match(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:int|interception) Return\s*)", play_desc,re.IGNORECASE)

		skip = re.match(r"((?:Timeout|Quarter|End))",play_desc,re.IGNORECASE)

		pass_simple = re.match(r"(.*(?:pass|complete|incomplete).*)", play_desc,re.IGNORECASE)
		run_simple = re.match(r"(.*(?:rush|run|sneak).*)", play_desc,re.IGNORECASE)
		sack_simple = re.match(r"(.*(?:sack|sacked).*)", play_desc,re.IGNORECASE)
		fumble_simple = re.match(r"(.*(?:fumbled|fumble).*)", play_desc,re.IGNORECASE)
		int_simple = re.match(r"(.*(?:int|intercepted|intercept).*)", play_desc,re.IGNORECASE)
		blocked_simple = re.match(r"(.*(?:block).*)", play_desc,re.IGNORECASE)
		penalty_simple = re.match(r"(.*(?:penalty).*)", play_desc,re.IGNORECASE)
		no_play_simple = re.match(r"(no play)", play_desc,re.IGNORECASE)
		penalty_simple = re.match(r"(.*(?:fg|Field goal).*)", play_desc,re.IGNORECASE)
		fake_simple = re.match(r"(.*(?:fake).*)", play_desc,re.IGNORECASE)
		yards_simple = re.compile(r"(.*(?P<yards>\d+)(?:yd|yard|yds|yards| yd| yard| yds| yards)/*)",re.IGNORECASE)
		TD_simple = re.match(r"(.*(?:TD|Touchdown).*)", play_desc,re.IGNORECASE)
		FG_simple = re.match(r"(.*(?:FG|Goal).*)", play_desc,re.IGNORECASE)
		on_side_simple = re.match(r"(.*(?:on-side|onside).*)", play_desc,re.IGNORECASE)
		punt_simple =  re.match(r"(.*(?:punt).*)", play_desc,re.IGNORECASE)
		kick_simple =  re.match(r"(.*(?:kickoff).*)", play_desc,re.IGNORECASE)
		loss_simple = re.match(r"(.*(?:loss).*)", play_desc,re.IGNORECASE)
		missed_simple = re.match(r"(.*(?:missed|wide|miss).*)", play_desc,re.IGNORECASE)
		made_simple = re.match(r"(.*(?:made|good).*)", play_desc,re.IGNORECASE)

		if fumble_return:
			self.Play_Type = "RUSH"
			play_desc = re.sub(re.escape(fumble_return.group(0)), "", play_desc)
			self.Receiver = fumble_return.group("returner")
			# get yards gained
			self.Yards_Gained = (-1)*int(fumble_return.group("yards"))
			play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			self.Print_Remaining(play_desc)
			return True

		if int_return:
			self.Play_Type = "Pass"
			play_desc = re.sub(re.escape(int_return.group(0)), "", play_desc)
			self.Receiver = int_return.group("returner")
			# get yards gained
			self.Yards_Gained = (-1)*int(int_return.group("yards"))
			play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			self.Print_Remaining(play_desc)
			return True


		if rush1 or rush2 or sack:
			self.Play_Type = "RUSH"

			# Get data from rush
			if rush1:
				play_desc = re.sub(re.escape(rush1.group(0)), "", play_desc)
				self.Rusher = rush1.group("rusher")
				# get yards gained
				(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg, yard_regex)
			elif rush2:
				play_desc = re.sub(re.escape(rush2.group(0)), "", play_desc)
				self.Rusher = rush2.group("rusher")
				# get yards gained
				self.Yards_Gained = int(rush2.group("yards"))
				#raw_input("RUSH2")
			elif sack:
				self.Play_Type = "SACK"
				play_desc = re.sub(re.escape(sack.group(0)), "", play_desc)
				self.Rusher = sack.group("passer")
				# get sacker
				sacker = sacker_regex.match(play_desc)
				if sacker:
					if sacker.group("sacker"):
						self.Sacker = sacker.group("sacker")
					else:
						self.Sacker = sacker.group("sacker_group")
					play_desc = re.sub(re.escape(sacker.group(0)), "", play_desc)
				# get yards lost
				(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg, yard_regex)

			# get rest of play data
			play_desc = self.Get_New_Position(play_desc, postn_regex)
			play_desc = self.Check_First_Down(play_desc, first_regex)
			play_desc = self.Check_Safety(play_desc, safe_regex)
			play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
			play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			# Print remaining characters
			self.Print_Remaining(play_desc)
			return True

		elif pass_cmp or pass_inc or pass_int or pass_td:
			self.Play_Type = "PASS"

			# Get data from pass
			if pass_cmp:
				play_desc = re.sub(re.escape(pass_cmp.group(0)), "", play_desc)
				self.Completion = 1
				self.Passer = pass_cmp.group("passer")
				# get receiver (at end of string)
				rcvr1 = rcvr1_regex.match(play_desc)
				if rcvr1:
					self.Receiver = rcvr1.group("receiver")
					play_desc = re.sub(re.escape(rcvr1.group(0)), "", play_desc)
				# get receiver (with yards gained)
				rcvr2 = rcvr2_regex.match(play_desc)
				if rcvr2:
					self.Receiver = rcvr2.group("receiver")
					play_desc = re.sub(re.escape(rcvr2.group(0)), "", play_desc)
				# get yards gained
				(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg, yard_regex)
				# get rest of play data
				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_First_Down(play_desc, first_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			elif pass_inc:
				play_desc = re.sub(re.escape(pass_inc.group(0)), "", play_desc)
				self.Passer = pass_inc.group("passer")
				# get intended receiver
				rcvr3 = rcvr3_regex.match(play_desc)
				if rcvr3:
					self.Receiver = rcvr3.group("receiver")
					play_desc = re.sub(re.escape(rcvr3.group(0)), "", play_desc)

			elif pass_int:
				play_desc = re.sub(re.escape(pass_int.group(0)), "", play_desc)
				self.Interception = 1
				self.Passer = pass_int.group("passer")
				# get interceptor
				intcptr = int_regex.match(play_desc)
				if intcptr:
					self.Interceptor = intcptr.group("interceptor")
					play_desc = re.sub(re.escape(intcptr.group(0)), "", play_desc)

			elif pass_td:
				play_desc = re.sub(re.escape(pass_td.group(0)), "", play_desc)
				self.Receiver = pass_td.group("receiver");
				self.Passer = pass_td.group("passer");
				self.Yards_Gained = int(pass_td.group("yards"))
				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			# Print remaining characters
			self.Print_Remaining(play_desc)
			return True


		elif punt or punt_blocked or punt_return:
			self.Play_Type = "PUNT"
			if punt:
				play_desc = re.sub(re.escape(punt.group(0)), "", play_desc)
				self.Punter = punt.group("punter")
				# get yards gained
				#(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
				play_desc = self.Get_Yards_Kicked(play_desc, yard_regex)

				kick_return = kick_return.match(play_desc)
				if kick_return:
					play_desc = re.sub(re.escape(kick_return.group(0)), "", play_desc)
					## TODO PROBABLY SHOULDN"T BE RECEIVER
					self.Receiver = kick_return.group("returner")
					(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
					play_desc = self.Get_Yards_Returned(play_desc,neg,yard_regex)

			if punt_blocked:
				play_desc = re.sub(re.escape(punt_blocked.group(0)), "", play_desc)
				self.Punter = punt_blocked.group("punter")
				self.Kick_Blocked = 1

			if fumble_return:
				play_desc = re.sub(re.escape(punt_return.group(0)), "", play_desc)
				self.Receiver = punt_return.group("returner")
				# get yards gained
				self.Yards_Gained = int(punt_return.group("yards"))
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)


			# get rest of play data
			play_desc = self.Get_New_Position(play_desc, postn_regex)
			play_desc = self.Check_Safety(play_desc, safe_regex)
			play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
			play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			# Print remaining characters
			self.Print_Remaining(play_desc)
			return True

		elif kickoff or kickoff_return:
			self.Play_Type = "KICKOFF"


			if kickoff:
				play_desc = re.sub(re.escape(kickoff.group(0)), "", play_desc)
				self.Kicker = kickoff.group("kicker")
				# get yards gained
				#(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
				play_desc = self.Get_Yards_Kicked(play_desc, yard_regex)

				kick_return = kick_return.match(play_desc)
				if kick_return:
					play_desc = re.sub(re.escape(kick_return.group(0)), "", play_desc)
					## TODO PROBABLY SHOULDN"T BE RECEIVER
					self.Receiver = kick_return.group("returner")
					(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)
					play_desc = self.Get_Yards_Returned(play_desc,neg,yard_regex)

			if kickoff_return:
				play_desc = re.sub(re.escape(kickoff_return.group(0)), "", play_desc)
				self.Receiver = kickoff_return.group("returner")
				# get yards gained
				self.Yards_Gained = int(kickoff_return.group("yards"))
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			# get rest of play data
			play_desc = self.Get_New_Position(play_desc, postn_regex)
			play_desc = self.Check_Safety(play_desc, safe_regex)
			play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
			play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)

			# Print remaining characters
			self.Print_Remaining(play_desc)
			return True

		elif fg1 or fg2:
			self.Play_Type = "FIELD GOAL"
			if fg1:

				self.Kicker = fg1.group("kicker")
				self.Kick_Yards = fg1.group("yards")
				play_desc = re.sub(re.escape(fg1.group(0)), "", play_desc)
				play_desc = self.Get_Kick_Good(play_desc,fg_good_regex)
			elif fg2:
				play_desc = self.Get_Kick_Good(play_desc,fg_good_regex)
			self.Print_Remaining(play_desc)
			return True

		elif penalty or penalty_no_play:

			#print "PENALTY"
			#print play_desc

			self.Play_Type = "PENALTY"
			self.No_Play = 1
			self.Penalty = 1
			if penalty:
				self.Penalty_Type = penalty.group("penalty")
				play_desc = re.sub(re.escape(penalty.group()),"",play_desc)

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_First_Down(play_desc, first_regex)
			if penalty_no_play:
				self.No_Play = 1
				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_First_Down(play_desc, first_regex)



			self.Print_Remaining(play_desc)
			return True

		else:
			##SIMPLE TIME!
			if pass_simple:
				self.Play_Type = "PASS"

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)
				play_desc = self.Check_Yards_Simple	(play_desc,yards_simple)
				if loss_simple:
					self.Yards_Gained *= -1

				if fumble_simple:
					self.Fumble = 1
				if int_simple:
					self.Interception = 1
				if TD_simple:
					if self.Fumble or self.Interception:
						self.Def_Touchdown = 1
					else:
						self.Off_Touchdown = 1
			elif run_simple:
				self.Play_Type = "RUSH"

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)
				play_desc = self.Check_Yards_Simple	(play_desc,yards_simple)
				if loss_simple:
					self.Yards_Gained *= -1

				if fumble_simple:
					self.Fumble = 1
				if TD_simple:
					if self.Fumble or self.Interception:
						self.Def_Touchdown = 1
					else:
						self.Off_Touchdown = 1

			elif sack_simple:
				self.Play_Type = "SACK"

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)
				play_desc = self.Check_Yards_Simple	(play_desc,yards_simple)

				self.Yards_Gained *= -1

				if fumble_simple:
					self.Fumble = 1
				if TD_simple:
					if self.Fumble or self.Interception:
						self.Def_Touchdown = 1
					else:
						self.Off_Touchdown = 1
			elif punt_simple:
				self.Play_Type = "Punt"

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)
				if loss_simple:
					self.Yards_Gained *= -1

				if fumble_simple:
					self.Fumble = 1
				if TD_simple:
					if self.Fumble or self.Interception:
						self.Def_Touchdown = 1
					else:
						self.Off_Touchdown = 1
				if blocked_simple:
					self.Kick_Blocked = 1
				if fake_simple:
					self.Play_Type = "RUSH"
			elif kick_simple or on_side_simple:
				self.Play_Type = "KICKOFF"

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)
				if loss_simple:
					self.Yards_Gained *= -1

				if fumble_simple:
					self.Fumble = 1
				if TD_simple:
					if self.Fumble or self.Interception:
						self.Def_Touchdown = 1
					else:
						self.Off_Touchdown = 1
				#if on_side_simple:
			elif FG_simple:
				self.Play_Type = "FIELD GOAL"

				play_desc = self.Get_New_Position(play_desc, postn_regex)
				play_desc = self.Check_Safety(play_desc, safe_regex)
				play_desc = self.Check_Fumble(play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex)
				play_desc = self.Check_TD(play_desc, prev_play, td_regex, expt_regex1)
				#play_desc = self.Check_Yards_Simple	(play_desc,yards_simple)
				if loss_simple:
					self.Yards_Gained *= -1
				if blocked_simple:
					self.Kick_Blocked = 1
					self.KICK_GOOD = 0
				else:
					if made_simple:
						self.KICK_GOOD = 1
					elif missed_simple:
						self.KICK_GOOD = 0
				if fumble_simple:
					self.Fumble = 1
				if TD_simple:
					if self.Fumble or self.Interception:
						self.Def_Touchdown = 1
					else:
						self.Off_Touchdown = 1

			else:
				if not skip:
					print "FULL PLAY NOT PARSED:"
					print play_desc



	# Prints unparsed characters
	def Print_Remaining(self, play_desc):
		return
		play_desc = re.sub(" .\Z|\.", "", play_desc)
		if len(play_desc) > 1:
			print "\nThis play wasn't parsed: "
			print play_desc
			self.Unparsed = play_desc
			# raw_input(play_desc)


	# Gets the down/distance/spot
	def Get_Play_Info(self, play_info):
		m = re.match(r"((?P<down>\d)(?:st|nd|rd|th) and (?P<dist>\d+|Goal) at (?:t(?P<team>\d+) (?P<pos>\d+)|(?P<fifty>50)))", play_info)
		if m:
			self.Down = int(m.group("down"))
			# Get spot
			try:
				self.Spot = int(m.group("fifty"))
			except:
				self.Spot = self.Get_Field_Pos(self.Offense, int(m.group("team")), int(m.group("pos")))
			# Get distance; if "and goal", use field position
			if m.group("dist") == "Goal":
				self.Distance = self.Spot
			else:
				self.Distance = int(m.group("dist"))


	# Checks for a loss of yards
	def Check_Yards_Lost(self, loss_regex, play_desc):
		loss = loss_regex.match(play_desc)
		if loss:
			neg = 1
			play_desc = re.sub(re.escape(loss.group(0)), "", play_desc)
		else:
			neg = 0
		return (neg, play_desc)


	# Gets the number of yards gained
	def Get_Yards_Gained(self, play_desc, neg, yard_regex):
		gain = yard_regex.match(play_desc)
		if gain:
			if gain.group("yards"):
				self.Yards_Gained = -1*int(gain.group("yards")) if neg == 1 else int(gain.group("yards"))
			elif gain.group("no_gain"):
				self.Yards_Gained = 0
			play_desc = re.sub(re.escape(gain.group(0)), "", play_desc)
		return play_desc

	def Get_Kick_Good(self,play_desc,good_regex):
		good = good_regex.match(play_desc)
		if good:
			self.KICK_GOOD = 1
			play_desc = re.sub(re.escape(good.group(0)),"",play_desc)
		else:
			self.KICK_GOOD = 0
			##TODO REGEX TO REMOVE SUB WHEN MISSED
		#play_desc = re.sub(re.escape(good.group(0)),"",play_desc)
		return play_desc

	# Gets the number of yards gained
	def Get_Yards_Kicked(self, play_desc, yard_regex):
		gain = yard_regex.match(play_desc)
		if gain:
			if gain.group("yards"):
				self.Kick_Yards = int(gain.group("yards"))
			elif gain.group("no_gain"):
				self.Kick_Yards = 0
			play_desc = re.sub(re.escape(gain.group(0)), "", play_desc)
		return play_desc

	def Get_Yards_Returned(self, play_desc,neg, yard_regex):
		gain = yard_regex.match(play_desc)
		if gain:
			if gain.group("yards"):
				self.Yards_Gained = -1*int(gain.group("yards")) if neg == 1 else int(gain.group("yards"))
			elif gain.group("no_gain"):
				self.Yards_Gained = 0
			play_desc = re.sub(re.escape(gain.group(0)), "", play_desc)
		return play_desc

	# Returns the real field position
	def Get_Field_Pos(self, offense, half, pos):
		if offense != half:
			return pos
		else:
			return 100 - pos


	# Checks for a safety
	def Get_New_Position(self, play_desc, postn_regex):
		position = postn_regex.match(play_desc)
		if position:
			if position.group("field_half"):
				if int(position.group("field_half")) == self.Offense:
					field_pos = int(position.group("yard_line"))
				else:
					field_pos = 100 - int(position.group("yard_line"))
			elif position.group("fifty"):
				field_pos = 50
			play_desc = re.sub(re.escape(position.group(0)), "", play_desc)
		return play_desc


	def Check_Yards_Simple(self,play_desc,yards_regex):
		first = yards_regex.search(play_desc)
		if first:
			if first.group('yards'):
				self.Yards_Gained = first.group('yards')
			play_desc = re.sub(re.escape(first.group(0)), "", play_desc)
		return play_desc

	# Checks for a safety
	def Check_First_Down(self, play_desc, first_regex):
		first = first_regex.search(play_desc)
		if first:
			self.First_Down = 1
			play_desc = re.sub(re.escape(first.group(0)), "", play_desc)
		return play_desc


	# Checks for a safety
	def Check_Safety(self, play_desc, safe_regex):
		safety = safe_regex.match(play_desc)
		if safety:
			self.Safety = 1
			play_desc = re.sub(re.escape(safety.group(0)), "", play_desc)
		return play_desc


	# Checks for a fumble/lost fumble
	def Check_Fumble(self, play_desc, fumb_regex, frcd_regex, flost_regex, fret_regex, postn_regex):
		fumble = fumb_regex.match(play_desc)
		if fumble:
			self.Fumble = 1
			play_desc = re.sub(re.escape(fumble.group(0)), "", play_desc)
		# check for forced
		forced = frcd_regex.match(play_desc)
		if self.Fumble == 1 and forced:
			self.Forced_Fum = forced.group("forcer")
			play_desc = re.sub(re.escape(forced.group(0)), "", play_desc)
		# check for fumble lost
		fum_lost = flost_regex.match(play_desc)
		if self.Fumble == 1 and fum_lost:
			if int(fum_lost.group("team")) != self.Offense:
				self.Fumble_Lost = 1
			play_desc = re.sub(re.escape(fum_lost.group(0)), "", play_desc)
		# check for distance returned
		fret = fret_regex.match(play_desc)
		if fret:
			Yards_Returned = fret.group("yards")
			play_desc = re.sub(re.escape(fret.group(0)), "", play_desc)
		fpos = postn_regex.match(play_desc)
		if fpos:
			if fpos.group("field_half"):
				if int(fpos.group("field_half")) == self.Offense:
					field_pos = int(fpos.group("yard_line"))
				else:
					field_pos = 100 - int(fpos.group("yard_line"))
			elif fpos.group("fifty"):
				field_pos = 50
			play_desc = re.sub(re.escape(fpos.group(0)), "", play_desc)
		return play_desc


	# Checks if a touchdown occurred
	def Check_TD(self, play_desc, prev_play, td_regex, expt_regex1):
		td = td_regex.search(play_desc)
		if td:
			# offesive TD
			if self.Off_Points >= prev_play.Off_Points + 6 and self.Offense == prev_play.Offense:
				self.Off_Touchdown = 1
				if self.Yards_Gained >= self.Distance:
					self.First_Down = 1
			# offensive TD on first play
			elif self.Off_Points >= prev_play.Def_Points + 6 and self.Offense == prev_play.Defense:
				self.Off_Touchdown = 1
				if self.Yards_Gained >= self.Distance:
					self.First_Down = 1
			# defensive TD
			elif self.Def_Points >= prev_play.Def_Points + 6 and self.Defense == prev_play.Defense:
				self.Def_Touchdown = 1
			# defensive TD on first play
			elif self.Def_Points >= prev_play.Off_Points + 6 and self.Defense == prev_play.Offense:
				self.Def_Touchdown = 1
			play_desc = re.sub(re.escape(td.group(0)), "", play_desc)
			# check for extra point
			extra_pt = expt_regex1.match(play_desc)
			if extra_pt:
				self.Extra_Pt_Att = 1
				self.Kick_Good = 1
				self.Kicker = extra_pt.group("kicker")
				play_desc = re.sub(re.escape(extra_pt.group(0)), "", play_desc)
		return play_desc


	# Returns an array of relavent information
	def Compile_Stats(self):
		OutputArray = []
		OutputArray.append(str(self.Game_Code))
		OutputArray.append(str(self.Play_Number))
		OutputArray.append(str(self.Period_Number))
		OutputArray.append(str(self.Drive_Start))
		OutputArray.append(str(self.Offense))
		OutputArray.append(str(self.Defense))
		OutputArray.append(str(self.Off_Points))
		OutputArray.append(str(self.Def_Points))
		OutputArray.append(str(self.Down))
		OutputArray.append(str(self.Distance))
		OutputArray.append(str(self.Spot))
		OutputArray.append(str(self.Play_Type))
		OutputArray.append(str(self.Drive_Number))
		OutputArray.append(str(self.Drive_Play))
		OutputArray.append(str(self.Play_Desc))
		OutputArray.append(str(self.Play_Result))
		OutputArray.append(str(self.Yards_Gained))
		OutputArray.append(str(self.Off_Touchdown))
		OutputArray.append(str(self.Def_Touchdown))
		OutputArray.append(str(self.First_Down))
		OutputArray.append(str(self.Completion))
		OutputArray.append(str(self.Interception))
		OutputArray.append(str(self.Fumble))
		OutputArray.append(str(self.Fumble_Lost))
		OutputArray.append(str(self.Kick_Good))
		OutputArray.append(str(self.TwoPt_Good))
		OutputArray.append(str(self.Safety))
		OutputArray.append(str(self.Kick_Yards))
		OutputArray.append(str(self.Touchback))
		OutputArray.append(str(self.Kickoff_OOB))
		OutputArray.append(str(self.Kickoff_Onsides))
		OutputArray.append(str(self.Kick_Blocked))
		OutputArray.append(str(self.Penalty))
		OutputArray.append(str(self.Penalty_Type))
		OutputArray.append(str(self.No_Play))
		OutputArray.append(str(self.Rusher))
		OutputArray.append(str(self.Passer))
		OutputArray.append(str(self.Receiver))
		OutputArray.append(str(self.Kicker))
		OutputArray.append(str(self.Forced_Fum))
		OutputArray.append(str(self.Interceptor))
		OutputArray.append(str(self.Sacker))
		OutputArray.append(str(self.Extra_Pt_Att))
		OutputArray.append(str(self.TwoPt_Att))
		OutputArray.append(str(self.Unparsed))
		return OutputArray


	# Returns the header for a play type
	def Header(self):
		OutputArray = []
		OutputArray.append("Game_Code")
		OutputArray.append("Play_Number")
		OutputArray.append("Period_Number")
		OutputArray.append("Drive_Start")
		OutputArray.append("Offense")
		OutputArray.append("Defense")
		OutputArray.append("Off_Points")
		OutputArray.append("Def_Points")
		OutputArray.append("Down")
		OutputArray.append("Distance")
		OutputArray.append("Spot")
		OutputArray.append("Play_Type")
		OutputArray.append("Drive_Number")
		OutputArray.append("Drive_Play")
		OutputArray.append("Play_Desc")
		OutputArray.append("Play_Result")
		OutputArray.append("Yards_Gained")
		OutputArray.append("Off_Touchdown")
		OutputArray.append("Def_Touchdown")
		OutputArray.append("First_Down")
		OutputArray.append("Completion")
		OutputArray.append("Interception")
		OutputArray.append("Fumble")
		OutputArray.append("Fumble_Lost")
		OutputArray.append("Kick_Good")
		OutputArray.append("TwoPt_Good")
		OutputArray.append("Safety")
		OutputArray.append("Kick_Yards")
		OutputArray.append("Touchback")
		OutputArray.append("Kickoff_OOB")
		OutputArray.append("Kickoff_Onsides")
		OutputArray.append("Kick_Blocked")
		OutputArray.append("Penalty")
		OutputArray.append("Penalty_Type")
		OutputArray.append("No_Play")
		OutputArray.append("Rusher")
		OutputArray.append("Passer")
		OutputArray.append("Receiver")
		OutputArray.append("Kicker")
		OutputArray.append("Forced_Fum")
		OutputArray.append("Interceptor")
		OutputArray.append("Sacker")
		OutputArray.append("Extra_Pt_Att")
		OutputArray.append("TwoPt_Att")
		OutputArray.append("Unparsed_Play_Desc")
		return OutputArray
