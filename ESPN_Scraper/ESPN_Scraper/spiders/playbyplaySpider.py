import scrapy
import re
import string
import os
import errno
import csv
from ESPN_Scraper.items import PBP_GameItem
from os import listdir
from os.path import isdir, isfile, join

year = 2015

# Make sure os path exists, create it if not
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Writes the contents of data to a .csv file
def Write_CSV(data, file_name):
	with open(file_name, "w+") as csvfile:
		data_writer = csv.writer(csvfile, lineterminator = '\n')
		data_writer.writerows(data)
		csvfile.close()

# SPIDER

def ESPN_id_to_Name(id):
	with open("ESPN_Scraper/ESPN_teams.csv") as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			try:
				if int(row[1]) == int(id):
					return row[0]
			except:
				continue
	print "THIS SHOULD NEVER HAPPEN!!! BAD!!!"
	return -1

class playbyplaySpider(scrapy.Spider):
	name = "playbyplay"
	allowed_domains = ["espn.go.com"]


	# Build URLs from scraped data
	#os.chdir(str(year)+"/scraped_games/week_1")
	start_urls = []
	for i in range(1, 17):
		folder = str(year) + "/scraped_games/week_" + str(i)
		make_sure_path_exists(folder)
		#folder = "../" + str(year) + "/scraped_games"
	#if 1 == 1:

		os.chdir(folder)
		for filename in os.listdir(os.getcwd()):
			new_game = PBP_GameItem()
			with open (filename, "r") as f:
				data = f.read()
				# Get start URL
				m = re.search(r"PBP: (?P<url>\S+)", data,re.IGNORECASE)
				if ''.join(e for e in m.group("url") if e.isalnum()) == "httpscoresespngocom":
					continue
				start_urls.append(m.group("url") + "&period=0")
				new_game['link'] = m.group("url") + "&period=0"
				# Get date
				m = re.search(r"Date: (?P<date>\d+)", data,re.IGNORECASE)
				new_game['date'] = m.group("date")
				# Get home
				m = re.search(r"Home: \D+ \((?P<code>\d+)\)", data,re.IGNORECASE)
				new_game['home_code'] = m.group("code")
				# Get visitor
				m = re.search(r"Away: \D+ \((?P<code>\d+)\)", data,re.IGNORECASE)
				new_game['away_code'] = m.group("code")
			infofile = ''.join(e for e in new_game['link'] if e.isalnum())
			make_sure_path_exists(os.getcwd() + "/../../tmpfiles/")
			#print os.getcwd() + "/../../tmpfiles/" + infofile + ".txt"
			with open(os.getcwd() + "/../../tmpfiles/" + infofile + ".txt", 'w') as f:
				f.write(new_game['link'] + "\n")
				f.write("Code: " + str(new_game['away_code']).zfill(4))
				f.write(str(new_game['home_code']).zfill(4))
				f.write(new_game['date'])
				f.close()
		os.chdir("../../..")



	def parse(self, response):
		# Get this game code from file
		with open(os.getcwd() + "/" +  str(year) + "/tmpfiles/" + ''.join(e for e in response.url if e.isalnum()) + ".txt") as f:
			data = f.read()
			m = re.search(r"Code: (?P<code>\d+)", data)
			code = str(m.group('code')).zfill(16)
		# Scrape play by play
		table = response.xpath('//div[contains(@id, "gamepackage-drives-wrap")]')
		rows = []
		visitor = int(code) / 1000000000000
		home = (int(code) / 100000000) % 1000
		date = int(code) % 100000000
		rows.append([code, "", visitor, home])

		away_score = 0
		home_score = 0
		prev_home_score = 0
		prev_away_score = 0

		for row in table.xpath('//li[contains(@class, "accordion-item")]'):

			## Handle header
			header = row.xpath('.//div[contains(@class, "accordion-header")]')
			## HALF TIME!
			if len(header) == 0:
				halfText = row.xpath('.//span[contains(@class, "post-play")]/text()').extract()[0]
				rows.append(['',halfText,away_score,home_score])
				continue

			prev_home_score = home_score
			prev_away_score = away_score
			driveTeam = header.xpath('.//img[contains(@class, "team-logo")]/@src').extract()
			try:
				driveTeam = str(driveTeam[0]).split('/')[-1].split('.')[0]
			except:
				print "Empty Drive in Game : " + str(code)
				break


			###############################
			## TODO NOTE THIS WILL PROBABLY BREAK WHEN ESPN FIXES IT
			## ESPN HAS HOME AND AWAY MIXED UP!!!!
			## SO WE REVERSE THEM FOR NOW
			#####################################
			header_home = header.xpath('.//span[contains(@class, "away")]')
			home_abv = header_home.xpath('.//span[contains(@class, "team-name")]/text()').extract()
			home_score = header_home.xpath('.//span[contains(@class, "team-score")]/text()').extract()[0]
			header_away = header.xpath('.//span[contains(@class, "home")]')
			away_abv = header_away.xpath('.//span[contains(@class, "team-name")]/text()').extract()
			away_score = header_away.xpath('.//span[contains(@class, "team-score")]/text()').extract()[0]
			drive_details = header.xpath('.//span[contains(@class, "drive-details")]/text()').extract()[0]
			drive_result = header.xpath('.//span[contains(@class, "headline")]/text()').extract()

			driveTeamName = ESPN_id_to_Name(driveTeam)
			rows.append([driveTeamName + " at 15:00",away_abv[0],home_abv[0]])

			## Handle Plays
			drive = row.xpath('.//ul[contains(@class, "drive-list")]')
			for play in drive.xpath('.//li'):
				place = play.xpath('.//h3/text()').extract()
				if place:
					place = place[0]
				else:
					place = ''

				desc = play.xpath('.//span[contains(@class, "post-play")]/text()').extract()
				try:
					desc = desc[0]
				except:
					print "No Play information, This is probably an ESPN BUG"
					continue
				last_item = row.xpath('.//span[contains(@class, "post-play")]/text()').extract()[-1]
				end = re.search("End of (?P<qrt>\d)(?:st|nd|rd|th) Quarter",last_item,re.IGNORECASE)
				if end:
					last_item = last_item = row.xpath('.//span[contains(@class, "post-play")]/text()').extract()[-2]
				try:
					if desc == last_item:
						rows.append([place,desc,away_score,home_score])
					else:
						rows.append([place,desc,prev_away_score,prev_home_score])
				except:
					print "Bad play In data: " + place + "  in driveTeamName"

			rows.append([driveTeamName + " DRIVE TOTALS: " + drive_details,away_abv[0],home_abv[0]])



			'''
			new_rows1 = [x.xpath('.//text()').extract() for x in row.xpath('.//td')]
			if len(new_rows1) > 0:
				rows.append(new_rows1)

			## handle header



			new_rows2 = [x.xpath('.//text()').extract() for x in row.xpath('.//th')]
			if len(new_rows2) > 0:
				if len(new_rows2) == 3:
					new_rows2 = [new_rows2[0], "", new_rows2[1], new_rows2[2]]
				rows.append(new_rows2)
			for i in range(0, len(rows[len(rows)-1])):
				rows[len(rows)-1][i] = ''.join([re.sub(r"\[u'\\xa0'\]|', |\[u'|u'|'\]|\[|\]", '', str(rows[len(rows)-1][i]))])

				'''
		if len(rows) > 1:
			newPath =  str(year)+ "/pbp/"
			if not os.path.exists(newPath):
					os.makedirs(newPath)

			Write_CSV(rows, newPath + str(visitor).zfill(4) + str(home).zfill(4) + str(date) + ".csv")


