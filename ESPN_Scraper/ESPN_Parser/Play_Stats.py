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


	#################################
	## TODO:
	## FAIR CATCH
	## BROKEN UP BY
	## CLEAN UP  XP TRIES
	## PENALTIES, WHEN THEY ARE ENFORCED AT PREVIOUS LOS (no play) They are Penalty, Else they are pass/Rush attempt
	## BETTER TD PARSING, USING SCORE IS UNRELIABLE IE http://espn.go.com/college-football/playbyplay?gameId=400756905

	# Extracts play data from play-by-play
	def Extract_Play_Data(self, play, prev_play):
		if len(play) < 2:
			return False
		play_info = play[0]
		play_desc = play[1]
		self.Play_Desc = play_desc

		# Get down and distance
		self.Get_Play_Info(play_info)

		if play_desc== "D. Sealey pass,to J. Epps for -4 yds":
			print "here"

		if self.Distance == 0 and self.Down != 0:
			print "ERROR"
		ESPN_parsed,play_desc = self.ESPN_Parser(play_desc,prev_play)
		simple_parsed = False
		if len(play_desc) > 0:
			simple_parsed,play_desc = self.Simple_Parser(play_desc,prev_play)

		if(ESPN_parsed and simple_parsed):
			print "needed both parsers, check this"

		if((ESPN_parsed or simple_parsed) and len(play_desc) > 0 and self.No_Play==0):
			self.Print_Remaining(play_desc)
			return True
		elif (ESPN_parsed or simple_parsed):
			return True
		elif len(play_desc) > 0:
			print "FULL PLAY NOT PARSED:"
			print play_desc
			self.Print_Remaining(play_desc)
			return False
		else:
			return False

	def ESPN_Parser(self,play_desc,prev_play):
		# Define regex types
		rush1 = re.search(r"((?P<rusher>\D+) (?:run|rush) ?(for)?)", play_desc,re.IGNORECASE)
		rush2 = re.search(r"((?P<rusher>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:run|rush)\s*)", play_desc,re.IGNORECASE)
		sack = re.search(r"((?P<passer>\D+) sacked by )", play_desc,re.IGNORECASE)
		pass_short = re.search(r"((?P<passer>\D+) pass,)", play_desc,re.IGNORECASE)
		pass_cmp = re.search(r"((?P<passer>\D+) pass complete(?:,| )?)", play_desc,re.IGNORECASE)
		pass_inc = re.search(r"((?P<passer>\D+) pass incomplete(?:,| )?)", play_desc,re.IGNORECASE)
		pass_int = re.search(r"((?P<passer>\D+) pass intercepted(?:,| )?)", play_desc,re.IGNORECASE)
		pass_td = re.search(r"((?P<receiver>\D+)(?P<yards>\d+) (?:yd|yard|yds|yards) pass from (?P<passer>\D+)\s*?(?=(\())?)", play_desc,re.IGNORECASE)
		rcvr1_regex = re.compile(r"(to (?P<receiver>\D+)\Z)",re.IGNORECASE)
		rcvr2_regex = re.compile(r"(to (?P<receiver>\D+) for\W+?)",re.IGNORECASE)
		rcvr3_regex = re.compile(r"(to (?P<receiver>\D+))",re.IGNORECASE)
		int_regex = re.compile(r"((?P<interceptor>\D+) return ? ?(for)?)",re.IGNORECASE)
		sacker_regex = re.compile(r"((?:(?P<sacker>\D+)|(?P<sacker_group>\D+ and \D+)) for )",re.IGNORECASE)
		punt = re.search(r"((?P<punter>\D+) (?:punt|punts) for\s*)", play_desc,re.IGNORECASE)
		punt_blocked = re.search(r"((?P<punter>\D+) (?:punt|punts) blocked\s*)", play_desc,re.IGNORECASE)
		punt_return = re.search(r"((?P<returner>\D+) ?(?P<yards>\d+) ?(?:yd|yard|yds|yards) ?(?:punt|punts) ?return)", play_desc,re.IGNORECASE)
		kickoff = re.search(r"((?P<kicker>\D+) (?:kickoff|kick) for\s*)", play_desc,re.IGNORECASE)

		fg1 = re.search(r"((?P<kicker>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:FG|field goal)\s*)", play_desc,re.IGNORECASE)
		fg2 = re.search(r"(FG|field goal)", play_desc,re.IGNORECASE)

		penalty_reg = re.compile(r"((?P<team>.*) ?penalty,? ?(?P<penalty>.*)\((?P<yds>.*)\)\s*)",re.IGNORECASE)
		penalty_no_play_reg = re.compile(r"(Penalty.*NO PLAY)",re.IGNORECASE)
		declined_reg = re.compile(r"declined",re.IGNORECASE)

		no_play = re.search(r"(.*no play.*)", play_desc,re.IGNORECASE)
		fumble_return =re.search(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:turnover|fumble) Return\s*)", play_desc,re.IGNORECASE)
		kickoff_return =re.search(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:kick|kickoff) Return\s*)", play_desc,re.IGNORECASE)
		#punt_return =re.search(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:punt) Return\s*)", play_desc,re.IGNORECASE)
		int_return =re.search(r"((?P<returner>\D+) (?P<yards>\d+) (?:yd|yard|yds|yards) (?:interception) Return\s*)", play_desc,re.IGNORECASE)
		kick_downed = re.compile(r"downed",re.IGNORECASE)
		fair_catch = re.compile(r"(fair catch by (?P<returner>\D+))",re.IGNORECASE)

		team_safety = re.search(r"(team safety)",play_desc,re.IGNORECASE)
		#kick_out_of_bounds = re.compile(r"((?:punt|kickoff|kick) out-of-bounds at (?:t(?P<team>\d+) (?P<pos>\d+)|(?P<fifty>50)))",re.IGNORECASE)

		Regex_match = False

		if no_play:
			self.No_Play = 1


		if fumble_return:
			self.Play_Type = "RUSH"
			self.Fumble = 1
			play_desc = re.sub(re.escape(fumble_return.group(0)), "", play_desc)
			self.Receiver = fumble_return.group("returner")
			# get yards gained
			self.Yards_Gained = (-1)*int(fumble_return.group("yards"))
			play_desc = self.Check_TD(play_desc, prev_play)

			Regex_match = True


		if int_return:
			self.Play_Type = "PASS"
			play_desc = re.sub(re.escape(int_return.group(0)), "", play_desc)
			self.Receiver = int_return.group("returner")
			# get yards gained
			self.Yards_Gained = (-1)*int(int_return.group("yards"))
			play_desc = self.Check_TD(play_desc, prev_play)

			Regex_match = True

		if team_safety:
			self.Play_Type = "RUSH"
			self.Safety = 1
			play_desc = re.sub(re.escape(team_safety.group(0)), "", play_desc)

		if rush1 or rush2 or sack:
			self.Play_Type = "RUSH"

			# Get data from rush
			if rush2:
				play_desc = re.sub(re.escape(rush2.group(0)), "", play_desc)
				self.Rusher = rush2.group("rusher")
				# get yards gained
				self.Yards_Gained = int(rush2.group("yards"))
			elif rush1:
				(neg, play_desc) = self.Check_Yards_Lost( play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg)
				play_desc = re.sub(re.escape(rush1.group(0)), "", play_desc)
				self.Rusher = rush1.group("rusher")
				# get yards gained



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
				(neg, play_desc) = self.Check_Yards_Lost( play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg)

			# get rest of play data
			play_desc = self.Get_New_Position(play_desc)
			play_desc = self.Check_First_Down(play_desc,prev_play)
			play_desc = self.Check_Safety(play_desc)
			play_desc = self.Check_Fumble(play_desc)
			play_desc = self.Check_TD(play_desc, prev_play)

			# Print remaining characters
			Regex_match = True

		if pass_cmp or pass_inc or pass_int or pass_td or pass_short:
			self.Play_Type = "PASS"

			# Get data from pass
			if pass_inc:
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


				play_desc = self.Get_Return(play_desc)
				intcptr = int_regex.match(play_desc)
				if intcptr:
					self.Interceptor = intcptr.group("interceptor")
					play_desc = re.sub(re.escape(intcptr.group(0)), "", play_desc)
				play_desc = self.Get_New_Position(play_desc)
				play_desc = self.Check_TD(play_desc, prev_play)
				(neg, play_desc) = self.Check_Yards_Lost(play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg)

			elif pass_td:
				self.Completion = 1
				play_desc = re.sub(re.escape(pass_td.group(0)), "", play_desc)
				self.Receiver = pass_td.group("receiver")
				self.Passer = pass_td.group("passer")
				self.Yards_Gained = int(pass_td.group("yards"))
				play_desc = self.Get_New_Position(play_desc)
				self.Passer = self.Check_TD(self.Passer,prev_play)
				#play_desc = self.Check_TD(play_desc, prev_play)

			elif pass_cmp or pass_short:
				pass_reg = pass_cmp if pass_cmp else pass_short
				play_desc = re.sub(re.escape(pass_reg.group(0)), "", play_desc)
				self.Completion = 1
				self.Passer = pass_reg.group("passer")
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
				(neg, play_desc) = self.Check_Yards_Lost(play_desc)
				play_desc = self.Get_Yards_Gained(play_desc, neg)
				# get rest of play data
				play_desc = self.Get_New_Position(play_desc)
				play_desc = self.Check_First_Down(play_desc,prev_play)
				play_desc = self.Check_Safety(play_desc)
				play_desc = self.Check_Fumble(play_desc)
				play_desc = self.Check_TD(play_desc, prev_play)

			# Print remaining characters
			Regex_match = True




		if punt or punt_blocked or punt_return:
			self.Play_Type = "PUNT"
			if punt:
				play_desc = re.sub(re.escape(punt.group(0)), "", play_desc)
				self.Punter = punt.group("punter")
				# get yards gained
				#(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)

				play_desc = self.Get_Yards_Kicked(play_desc)
				play_desc = self.Check_Kick_OOB(play_desc)
				play_desc = self.Check_Kick_Downed(play_desc)
				play_desc = self.Check_Touchback(play_desc)
				play_desc = self.Get_Return(play_desc)

			if punt_blocked:
				play_desc = re.sub(re.escape(punt_blocked.group(0)), "", play_desc)
				self.Punter = punt_blocked.group("punter")
				self.Kick_Blocked = 1

			if fumble_return:
				play_desc = re.sub(re.escape(punt_return.group(0)), "", play_desc)
				self.Receiver = punt_return.group("returner")
				# get yards gained
				self.Yards_Gained = int(punt_return.group("yards"))
				play_desc = self.Check_TD(play_desc, prev_play)


			# get rest of play data
			downed = kick_downed.match(play_desc)
			if downed:
				play_desc = re.sub(re.escape(downed.group(0)), "", play_desc)

			fair = fair_catch.search(play_desc)
			if fair:
				self.Receiver = fair.group("returner")
				play_desc = re.sub(re.escape(fair.group(0)), "", play_desc)
			play_desc = self.Get_New_Position(play_desc)
			play_desc = self.Check_Safety(play_desc)
			play_desc = self.Check_Fumble(play_desc)
			play_desc = self.Check_TD(play_desc, prev_play)

			# Print remaining characters
			Regex_match = True

		if fg1 or fg2:
			self.Play_Type = "FIELD GOAL"
			if fg1:

				self.Kicker = fg1.group("kicker")
				self.Kick_Yards = fg1.group("yards")
				play_desc = re.sub(re.escape(fg1.group(0)), "", play_desc)

			play_desc = self.Get_Kick_Good(play_desc)

			Regex_match = True

		if kickoff or kickoff_return:
			self.Play_Type = "KICKOFF"

			if kickoff:
				play_desc = re.sub(re.escape(kickoff.group(0)), "", play_desc)
				self.Kicker = kickoff.group("kicker")
				# get yards gained
				#(neg, play_desc) = self.Check_Yards_Lost(loss_regex, play_desc)

				play_desc = self.Get_Yards_Kicked(play_desc)
				play_desc = self.Check_Kick_OOB(play_desc)
				play_desc = self.Check_Kick_Downed(play_desc)
				play_desc = self.Check_Touchback(play_desc)
				play_desc = self.Get_Return(play_desc)

			if kickoff_return:
				play_desc = re.sub(re.escape(kickoff_return.group(0)), "", play_desc)
				self.Receiver = kickoff_return.group("returner")
				# get yards gained
				self.Yards_Gained = int(kickoff_return.group("yards"))
				play_desc = self.Check_TD(play_desc, prev_play)

			# get rest of play data
			downed = kick_downed.match(play_desc)
			if downed:
				play_desc = re.sub(re.escape(downed.group(0)), "", play_desc)

			play_desc = self.Get_New_Position(play_desc)
			play_desc = self.Check_Safety(play_desc)
			play_desc = self.Check_Fumble(play_desc)
			play_desc = self.Check_TD(play_desc, prev_play)

			# Print remaining characters

			Regex_match = True

		penalty = penalty_reg.search(play_desc)
		penalty_no_play = penalty_no_play_reg.search(play_desc)

		if penalty or penalty_no_play:

			declined = declined_reg.search(play_desc)
			if declined:
				play_desc = re.sub(re.escape(declined.group(0)),"",play_desc)
			else:
				self.Penalty = 1

			if self.Play_Type == "":
				self.No_Play = 1
				self.Play_Type = "PENALTY"

			if penalty:
				self.Penalty_Type = penalty.group("penalty")
				play_desc = re.sub(re.escape(penalty.group(0)),"",play_desc)

				play_desc = self.Get_New_Position(play_desc)
				play_desc = self.Check_First_Down(play_desc,prev_play)
				#play_desc = re.sub(re.escape(penalty.group(0)), "", play_desc)
			if penalty_no_play:
				self.No_Play = 1
				play_desc = self.Get_New_Position(play_desc)
				play_desc = self.Check_First_Down(play_desc,prev_play)
			Regex_match = True



		return Regex_match,play_desc

	def Simple_Parser(self,play_desc,prev_play):
		skip = re.search(r"((?:Timeout|Quarter|End))",play_desc,re.IGNORECASE)

		pass_trigger = re.search(r"((?:pass|complete|incomplete|completion|spike))", play_desc,re.IGNORECASE)
		incomplete_simple =  re.compile(r"((?:incomplete|incompletion|batted away|knocked away|dropped))",re.IGNORECASE)
		complete_simple = re.compile(r"((?:complete))",re.IGNORECASE)
		run_trigger = re.search(r"((?:rush|run|sneak|kneel|scramble))", play_desc,re.IGNORECASE)
		run_trigger2 = re.match(r"((?P<runner>\S+) to )", play_desc,re.IGNORECASE)
		receiver_simple = re.compile(r"((?:intended for|to) (?P<receiver>.*)/s?(for)?\.?)",re.IGNORECASE)
		sack_trigger = re.search(r"((?:sack|sacked))", play_desc,re.IGNORECASE)
		fumble_simple = re.search(r"((?:fumbled|fumble|fumbles))", play_desc,re.IGNORECASE)
		int_simple = re.compile(r"((?:intercepted|intercept))",re.IGNORECASE)
		blocked_simple = re.search(r"((?:block))", play_desc,re.IGNORECASE)
		penalty_simple = re.search(r"((?:penalty))", play_desc,re.IGNORECASE)
		no_play_simple = re.search(r"(no play)", play_desc,re.IGNORECASE)
		fake_simple = re.search(r"((?:fake).*)", play_desc,re.IGNORECASE)
		yards_simple = re.compile(r"(.*(?P<yards>\d+)(?:yd|yard|yds|yards| yd| yard| yds| yards)/*)",re.IGNORECASE)
		TD_simple = re.search(r"((?:TD|Touchdown))", play_desc,re.IGNORECASE)
		FG_simple = re.search(r"((?:FG|Field Goal))", play_desc,re.IGNORECASE)
		on_side_simple = re.search(r"((?:on-side|onside))", play_desc,re.IGNORECASE)
		punt_simple =  re.search(r"((?:punt))", play_desc,re.IGNORECASE)
		safety_simple =  re.search(r"((?:safety))", play_desc,re.IGNORECASE)
		kick_simple =  re.search(r"((?:kickoff|kicks))", play_desc,re.IGNORECASE)
		loss_simple = re.search(r"((?:loss))", play_desc,re.IGNORECASE)
		missed_simple = re.search(r"((?:missed|wide|miss))", play_desc,re.IGNORECASE)
		made_simple = re.search(r"((?:made|good))", play_desc,re.IGNORECASE)
		touchback_simple =re.compile(r"((?:touchback))",re.IGNORECASE)
		fair_catch_simple = re.compile(r"((?:fair catch))",re.IGNORECASE)
		first_down_simple =re.search(r"((?:1st|first)\s?down)", play_desc,re.IGNORECASE)

		inDesc = play_desc

		#breakpoint = re.search(r"(Jamardre Cobb)",play_desc,re.IGNORECASE)
		#if breakpoint:
		#	print "HERE"

		if safety_simple:
			self.Play_Type = "RUSH"
			self.Safety = 1
			play_desc = re.sub(re.escape(safety_simple.group(0)), "", play_desc)

		if pass_trigger:
			self.Play_Type = "PASS"
			incomplete = incomplete_simple.search(play_desc)
			if incomplete:
				self.Completion = 0
				play_desc = re.sub(re.escape(incomplete.group(0)), "", play_desc)
			complete = complete_simple.search(play_desc)
			if complete:
				self.Completion = 1
				play_desc = re.sub(re.escape(complete.group(0)), "", play_desc)

			receiver_regex = receiver_simple.search(play_desc)
			if receiver_regex:
				self.Receiver = receiver_regex.group("receiver")
				play_desc = re.sub(re.escape(receiver_regex.group(0)), "", play_desc)

			interception = int_simple.search(play_desc)
			if interception:
				self.Interception = 1
				self.Completion = 0
				play_desc = re.sub(re.escape(interception.group(0)), "", play_desc)
			play_desc = re.sub(re.escape(pass_trigger.group(0)), "", play_desc)



		elif run_trigger or run_trigger2:
			self.Play_Type = "RUSH"

			if run_trigger:
				play_desc = re.sub(re.escape(run_trigger.group(0)), "", play_desc)
			elif run_trigger2:
				self.Rusher = run_trigger2.group("runner")
				play_desc = re.sub(re.escape(run_trigger2.group(0)), "", play_desc)




		elif sack_trigger:
			self.Play_Type = "SACK"
			play_desc = re.sub(re.escape(sack_trigger.group(0)), "", play_desc)

		elif punt_simple:
			self.Play_Type = "PUNT"
			play_desc = re.sub(re.escape(punt_simple.group(0)), "", play_desc)

			touchback = touchback_simple.search(play_desc)
			if touchback:
				self.Touchback = 1
				play_desc = re.sub(re.escape(touchback.group(0)), "", play_desc)

			fair_catch = fair_catch_simple.search(play_desc)
			if fair_catch:
				#self.
				play_desc = re.sub(re.escape(fair_catch.group(0)), "", play_desc)


			if blocked_simple:
				self.Kick_Blocked = 1
			if fake_simple:
				play_desc = re.sub(re.escape(fake_simple.group(0)), "", play_desc)
				self.Play_Type = "RUSH"

		elif FG_simple:
			self.Play_Type = "FIELD GOAL"
			play_desc = re.sub(re.escape(FG_simple.group(0)), "", play_desc)

			if fake_simple:
				play_desc = re.sub(re.escape(fake_simple.group(0)), "", play_desc)
				self.Play_Type = "RUSH"

			elif blocked_simple:
				play_desc = re.sub(re.escape(blocked_simple.group(0)), "", play_desc)
				self.Kick_Blocked = 1
				self.Kick_Good = 0
			else:
				if made_simple:
					play_desc = re.sub(re.escape(made_simple.group(0)), "", play_desc)
					self.Kick_Good = 1
				if missed_simple:
					play_desc = re.sub(re.escape(missed_simple.group(0)), "", play_desc)
					self.Kick_Good = 0


		elif kick_simple or on_side_simple:
			self.Play_Type = "KICKOFF"
			if kick_simple:
				play_desc = re.sub(re.escape(kick_simple.group(0)), "", play_desc)
			if on_side_simple:
				play_desc = re.sub(re.escape(on_side_simple.group(0)), "", play_desc)



		if first_down_simple:
			self.First_Down = 1
			play_desc = re.sub(re.escape(first_down_simple.group(0)), "", play_desc)

		if penalty_simple:
			self.Penalty = 1
			play_desc = re.sub(re.escape(penalty_simple.group(0)), "", play_desc)
			if self.Play_Type == "":
				self.No_Play = 1
				self.Play_Type = "PENALTY"

		if no_play_simple:
			self.No_Play = 1
			play_desc = re.sub(re.escape(no_play_simple.group(0)), "", play_desc)



		if skip:
			return False,''
		else:

			if self.Play_Type == '':
				print "Rush fallback, don't trust this"
				self.Play_Type ='RUSH'

			(neg, play_desc) = self.Check_Yards_Lost( play_desc)
			play_desc = self.Get_Yards_Gained(play_desc,neg)
			play_desc = self.Get_New_Position(play_desc)
			play_desc = self.Check_Safety(play_desc)
			play_desc = self.Check_Fumble(play_desc)
			play_desc = self.Check_TD(play_desc,prev_play)
			play_desc = self.Compute_First_Down(play_desc,prev_play)


			if fumble_simple:
				play_desc = re.sub(re.escape(fumble_simple.group(0)), "", play_desc)
				self.Fumble = 1
			if TD_simple:
				play_desc = re.sub(re.escape(TD_simple.group(0)), "", play_desc)
				if self.Fumble or self.Interception:
					self.Def_Touchdown = 1
				else:
					self.Off_Touchdown = 1

		return not inDesc == play_desc,play_desc


	# Prints unparsed characters
	def Print_Remaining(self, play_desc):
		play_desc = re.sub(" .\Z|\.", "", play_desc)
		if len(play_desc) > 1:
			# print "\nThis play wasn't parsed: "
			# print play_desc
			self.Unparsed = play_desc
			# raw_input(play_desc)

	# Gets the down/distance/spot
	def Get_Play_Info(self, play_info):
		m = re.search(r"((?P<down>\d)(?:st|nd|rd|th) and (?P<dist>\d+|Goal) at (?:t(?P<team>\d+) (?P<pos>\d+)|(?P<fifty>50)))", play_info)
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
				if int(m.group("dist")) == 0:
					self.Distance = self.Spot
				else:
					self.Distance = int(m.group("dist"))


	# Checks for a loss of yards
	def Check_Yards_Lost(self, play_desc):
		loss_regex = re.compile(r"(a loss of\s*)")
		loss = loss_regex.match(play_desc)
		if loss:
			neg = 1
			play_desc = re.sub(re.escape(loss.group(0)), "", play_desc)
		else:
			neg = 0
		return (neg, play_desc)


	# Gets the number of yards gained
	def Get_Yards_Gained(self, play_desc,neg):
		yard_regex = re.compile(r"(((?P<negative>\-)?(?P<yards>\d+) (?:yards|yard|yds|yd))|(?P<no_gain>no gain))",re.IGNORECASE)
		gain = yard_regex.search(play_desc)
		if gain:
			if gain.group("negative"):
				 neg = 1
			if gain.group("yards"):
				self.Yards_Gained = -1*int(gain.group("yards")) if neg == 1 else int(gain.group("yards"))
			elif gain.group("no_gain"):
				self.Yards_Gained = 0
			play_desc = re.sub(re.escape(gain.group(0)), "", play_desc)
		return play_desc

	def Get_Return(self,play_desc):
		kick_return_regex = re.compile(r"((?P<returner>\D+) (?:return|returns) for\s*)",re.IGNORECASE)
		kick_return = kick_return_regex.match(play_desc)
		if kick_return:
			play_desc = re.sub(re.escape(kick_return.group(0)), "", play_desc)
			## TODO PROBABLY SHOULDN"T BE RECEIVER
			self.Receiver = kick_return.group("returner")
			(neg, play_desc) = self.Check_Yards_Lost( play_desc)
			play_desc = self.Get_Yards_Gained(play_desc,neg)
		return play_desc

	def Get_Kick_Good(self,play_desc):

		fg_no_good_regex = re.compile(r"(no good)",re.IGNORECASE)
		no_good = fg_no_good_regex.search(play_desc)

		fg_good_regex = re.compile(r"((?:Good|Made))",re.IGNORECASE)
		good = fg_good_regex.search(play_desc)
		if no_good:
			self.Kick_Good = 0
			play_desc = re.sub(re.escape(no_good.group(0)),"",play_desc)
		elif good:
			self.Kick_Good = 1
			play_desc = re.sub(re.escape(good.group(0)),"",play_desc)


		fg_bad_regex = re.compile(r"(Missed)",re.IGNORECASE)
		bad = fg_bad_regex.search(play_desc)
		if bad:
			self.Kick_Good = 0
			play_desc = re.sub(re.escape(bad.group(0)),"",play_desc)
		else:
			fg_blocked_regex = re.compile(r"((?:blocked|block))",re.IGNORECASE)
			blocked = fg_blocked_regex.search(play_desc)
			if blocked:
				self.Kick_Good = 0
				self.Kick_Blocked = 1
				play_desc = re.sub(re.escape(blocked.group(0)),"",play_desc)
		return play_desc

	# Gets the number of yards gained
	def Get_Yards_Kicked(self, play_desc):
		yard_regex = re.compile(r"(((?P<yards>\d+) (?:yards|yard|yds|yd)\W+)|(?P<no_gain>no gain)\W+)")
		gain = yard_regex.match(play_desc)
		if gain:
			if gain.group("yards"):
				self.Kick_Yards = int(gain.group("yards"))
			elif gain.group("no_gain"):
				self.Kick_Yards = 0
			play_desc = re.sub(re.escape(gain.group(0)), "", play_desc)
		yard_regex2 = re.compile(r"(((?P<yards>\d+) (?:yards|yard|yds|yd))|(?P<no_gain>no gain))")
		gain = yard_regex2.match(play_desc)
		if gain:
			if gain.group("yards"):
				self.Kick_Yards = int(gain.group("yards"))
			elif gain.group("no_gain"):
				self.Kick_Yards = 0
			play_desc = re.sub(re.escape(gain.group(0)), "", play_desc)
		return play_desc



	# Returns the real field position
	def Get_Field_Pos(self, offense, half, pos):
		if offense != half:
			return pos
		else:
			return 100 - pos


	def Check_Touchback(self, play_desc):
		touchback_regex = re.compile(r"((?:for a|a|) touchback)",re.IGNORECASE)
		touchback = touchback_regex.match(play_desc)
		if touchback:
			self.Touchback = 1
			play_desc = re.sub(re.escape(touchback.group(0)), "", play_desc)
		return play_desc


	def Check_Kick_OOB(self, play_desc):
		kick_out_of_bounds_regex = re.compile(r"((?:punt|kickoff|kick) out\-of\-bounds)",re.IGNORECASE)#(?: at | at the )(?:t(?P<team>\d+) (?P<pos>\d+)|(?P<fifty>50)?\*))",re.IGNORECASE)
		#kick_out_of_bounds_regex2 = re.compile(r"(.*out\-of\-bounds.*)",re.IGNORECASE)
		kick_out_of_bounds = kick_out_of_bounds_regex.match(play_desc)
		if kick_out_of_bounds:
			self.Kickoff_OOB = 1
			play_desc = re.sub(re.escape(kick_out_of_bounds.group(0)), "", play_desc)
		return play_desc

	def Check_Kick_Downed(self, play_desc):
		kick_downed_regex = re.compile(r"(downed(?: at | at the )(?:t(?P<team>\d+) (?P<pos>\d+)|(?P<fifty>50)?\*))",re.IGNORECASE)
		#kick_out_of_bounds_regex2 = re.compile(r"(.*out\-of\-bounds.*)",re.IGNORECASE)
		kick_downed = kick_downed_regex.match(play_desc)
		if kick_downed:
			#self.Kick = 1
			play_desc = re.sub(re.escape(kick_downed.group(0)), "", play_desc)
		return play_desc


	# Gets new Position
	def Get_New_Position(self, play_desc):
		postn_regex = re.compile(r"(to (the)?\s?t(?P<field_half>\d+) (?P<yard_line>\d+)(?:,)?(?:\s+)?)|(to (the)?\s?(?P<fifty>50) (?:yard|yd) line(?:,)?\s*)")
		position = postn_regex.match(play_desc)
		if position:
			if position.group("field_half"):
				if int(position.group("field_half")) == self.Offense:
					field_pos = int(position.group("yard_line"))
				elif int(position.group("field_half")) == self.Defense:
					field_pos = 100 - int(position.group("yard_line"))
				else:
					print "MAJOR ERROR, WE ARE GUESSING HALF OF THE FIELD"

			elif position.group("fifty"):
				field_pos = 50
			play_desc = re.sub(re.escape(position.group(0)), "", play_desc)

		return play_desc


	def Check_Yards_Simple(self,play_desc):
		#yards_regex = re.compile(r"(.*(?P<yards>\d+)(?:yd|yard|yds|yards| yd| yard| yds| yards)/*)",re.IGNORECASE)
		yards_regex = re.compile(r"(((?P<yards>\d+) (?:yd|yard|yds|yards| yd| yard| yds| yards)\W+)|(?P<no_gain>no gain)\W+)")
		first = yards_regex.search(play_desc)
		if first:
			if first.group('yards'):
				self.Yards_Gained = int(first.group('yards'))
			play_desc = re.sub(re.escape(first.group(0)), "", play_desc)
		return play_desc

	def Compute_First_Down(self,play_desc,prev_play):
		if self.Offense == prev_play.Offense:
			if self.Down == 1:
				if self.Spot < prev_play.Spot - prev_play.Distance:
					prev_play.First_Down = 1
		return play_desc


	# Checks for a First Down
	def Check_First_Down(self, play_desc,prev_play):
		first_regex = re.compile(r"((?:for a|a) (?P<fd>1ST down))", re.IGNORECASE)
		first = first_regex.search(play_desc)
		if first:
			self.First_Down = 1
			play_desc = re.sub(re.escape(first.group(0)), "", play_desc)

		self.Compute_First_Down(play_desc,prev_play)
		return play_desc



	# Checks for a safety
	def Check_Safety(self, play_desc):
		safe_regex = re.compile(r"(for a (?P<safety>SAFETY)\s*)")
		safety = safe_regex.search(play_desc)
		if safety:
			self.Safety = 1
			play_desc = re.sub(re.escape(safety.group(0)), "", play_desc)
		return play_desc


	# Checks for a fumble/lost fumble
	def Check_Fumble(self, play_desc):
		fumb_regex = re.compile(r"(\D+ (?P<fumble>fumbled)(?:\W\s)?)")
		frcd_regex = re.compile(r"(forced by (?P<forcer>\D+),\s)")
		flost_regex = re.compile(r"(recovered by t?(?P<team>\w) ?(?:(?P<player>[^,]+))?(?:\W\s)?)")
		fret_regex = re.compile(r"(return for (?P<yards>\d+) (?:yards|yard|yds|yd)\s*)")
		fumble = fumb_regex.match(play_desc)
		if fumble:
			self.Fumble = 1
			play_desc = re.sub(re.escape(fumble.group(0)), "", play_desc)
		# check for forced
		forced = frcd_regex.search(play_desc)
		if self.Fumble == 1 and forced:
			self.Forced_Fum = forced.group("forcer")
			play_desc = re.sub(re.escape(forced.group(0)), "", play_desc)
		# check for fumble lost
		fum_lost = flost_regex.search(play_desc)
		if self.Fumble == 1 and fum_lost:
			try:
				if int(fum_lost.group("team")) != self.Offense:
					self.Fumble_Lost = 1
			except:
				print "We didn't correctly replace This team abbreviation, Fumble recovery will need to determined afterward"
			play_desc = re.sub(re.escape(fum_lost.group(0)), "", play_desc)
		# check for distance returned
		fret = fret_regex.search(play_desc)
		if fret:
			Yards_Returned = fret.group("yards")
			play_desc = re.sub(re.escape(fret.group(0)), "", play_desc)
		return play_desc


	# Checks if a touchdown occurred
	def Check_TD(self, play_desc, prev_play):

		forceTD = False
		td_regex = re.compile(r"((?:a|for a|) (?P<td>TD|TOUCHDOWN))", re.IGNORECASE)
		td = td_regex.search(play_desc)
		if td:
			play_desc = re.sub(re.escape(td.group(0)), "", play_desc)
			forceTD = True

		expt_regex1 = re.compile(r"((?:, )?(?: )?\((?P<kicker>\D+) KICK\))", re.IGNORECASE)
		extra_pt = expt_regex1.search(play_desc)
		if extra_pt:
			self.Extra_Pt_Att = 1
			self.Kick_Good = 1
			self.Kicker = extra_pt.group("kicker")
			play_desc = re.sub(re.escape(extra_pt.group(0)), "", play_desc)
			forceTD = True
		twopt_regex1 = re.compile(r"(\(.*(?:2pt|2 point|2-point|two point|two-point)(?: | conversion).*\))", re.IGNORECASE)
		two_pt = twopt_regex1.search(play_desc)
		if two_pt:
			self.TwoPt_Att = 1
			twopt_fail_regex1 = re.search(r"(\(.*(?:fail|failed|defense).*\))",play_desc, re.IGNORECASE)
			if twopt_fail_regex1:
				self.TwoPt_Good = 0
			else:
				self.TwoPt_Good = 1
			play_desc = re.sub(re.escape(two_pt.group(0)), "", play_desc)
			forceTD = True


		# offesive TD
		if self.Off_Points >= prev_play.Off_Points + 6 and self.Offense == prev_play.Offense:
			self.Off_Touchdown = 1
			play_desc = self.Get_Kick_Good(play_desc)
			if self.Yards_Gained >= self.Distance:
				self.First_Down = 1
		# offensive TD on first play
		elif self.Off_Points >= prev_play.Def_Points + 6 and self.Offense == prev_play.Defense:
			self.Off_Touchdown = 1
			play_desc = self.Get_Kick_Good(play_desc)
			if self.Yards_Gained >= self.Distance:
				self.First_Down = 1
		# defensive TD
		elif self.Def_Points >= prev_play.Def_Points + 6 and self.Defense == prev_play.Defense:
			self.Def_Touchdown = 1
			play_desc = self.Get_Kick_Good(play_desc)
		# defensive TD on first play
		elif self.Def_Points >= prev_play.Off_Points + 6 and self.Defense == prev_play.Offense:
			self.Def_Touchdown = 1
			play_desc = self.Get_Kick_Good(play_desc)
		# check for extra point

			if self.Def_Touchdown == 0 and self.Off_Touchdown ==0 and forceTD == True:
				print "shouldn't ever happen"

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
		OutputArray.append("Game Code")
		OutputArray.append("Play Number")
		OutputArray.append("Period Number")
		OutputArray.append("Drive Start")
		OutputArray.append("Offense Team Code")
		OutputArray.append("Defense Team Code")
		OutputArray.append("Offense Points")
		OutputArray.append("Defense Points")
		OutputArray.append("Down")
		OutputArray.append("Distance")
		OutputArray.append("Spot")
		OutputArray.append("Play Type")
		OutputArray.append("Drive Number")
		OutputArray.append("Drive Play")
		OutputArray.append("Play Desc")
		OutputArray.append("Play Result")
		OutputArray.append("Yards Gained")
		OutputArray.append("Off Touchdown")
		OutputArray.append("Def Touchdown")
		OutputArray.append("First Down")
		OutputArray.append("Completion")
		OutputArray.append("Interception")
		OutputArray.append("Fumble")
		OutputArray.append("Fumble Lost")
		OutputArray.append("Kick Good")
		OutputArray.append("TwoPt Good")
		OutputArray.append("Safety")
		OutputArray.append("Kick Yards")
		OutputArray.append("Touchback")
		OutputArray.append("Kickoff OOB")
		OutputArray.append("Kickoff Onsides")
		OutputArray.append("Kick Blocked")
		OutputArray.append("Penalty")
		OutputArray.append("Penalty Type")
		OutputArray.append("No Play")
		OutputArray.append("Rusher")
		OutputArray.append("Passer")
		OutputArray.append("Receiver")
		OutputArray.append("Kicker")
		OutputArray.append("Forced_Fum")
		OutputArray.append("Interceptor")
		OutputArray.append("Sacker")
		OutputArray.append("Extra Pt Att")
		OutputArray.append("TwoPt Att")
		OutputArray.append("Unparsed Play Desc")
		return OutputArray