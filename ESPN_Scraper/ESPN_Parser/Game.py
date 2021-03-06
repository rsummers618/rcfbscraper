import re

# Holds the data for a gane
class Game:


	# Constructor
	def __init__(self, pbp_data):
		self.Code = pbp_data[0][0]
		self.Date = int(long(self.Code) % 1e8)
		self.Current_Qrt = 1
		self.Visitor_Pts = 0
		self.Home_Pts = 0

	# Sets the quarter if a new one occurs
	def Set_Quarter(self, play):
		m = re.match(r"(?P<qrt>\d)(?:st|nd|rd|th) Quarter Play-by-Play", play[0])
		if m:
			if self.Current_Qrt == int(m.group("qrt")):
				return False
			else:
				self.Current_Qrt = int(m.group("qrt"))
				return True
		else:
			m =re.match(r"End of (?P<qrt>\d)(?:st|nd|rd|th) Quarter", play[1])
			if m:
				if self.Current_Qrt == int(m.group("qrt")) + 1:
					return False
				else:
					self.Current_Qrt = int(m.group("qrt")) + 1
					return True
		return True

	# Sets the point totals
	def Check_Points(self, play):
		if len(play) > 3:
			visitor = re.match(r"\b\d+\b", play[2])
			home = re.match(r"\b\d+\b", play[3])
			if visitor and int(visitor.group(0)) > self.Visitor_Pts:
				self.Visitor_Pts = int(visitor.group(0))
			if home and int(home.group(0)) > self.Home_Pts:
				self.Home_Pts = int(home.group(0))
