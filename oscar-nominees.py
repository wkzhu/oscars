import requests
from lxml import etree
import csv
import re
import sys
reload(sys)
sys.setdefaultencoding("utf8")
# -*- coding: utf-8 -*-

def format(string):
	if string != 'N/A':
		formattedResult = string.replace(',', '')
		formattedResult = re.search(r"[-+]?\d*\.*\d+",formattedResult).group()
		formattedResult = float(formattedResult)
		if 'mil' in string:
			formattedResult *= 1000000
		elif 'bil' in string:
			formattedResult *= 1000000000
		# catch numbers in GBP
		if u'\xa3' in string:
			return formattedResult*1.57
		else:
			return formattedResult

# add the ordinal (i-th) award
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

url = "http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture"
res = requests.get(url)

nomineeList = []
budgets = []
revenues = []

i = 0
for i in range (0,87):
	ith = ordinal(i+1)
	parser = etree.HTMLParser()
	root = etree.fromstring(res.content,parser)
	nominees = root.xpath("//table[@class='wikitable']/caption/a[contains(text(),'("+ith+")')]/../../tr/following-sibling::tr/td/i/a")
	# note that the first nominee in the list is the winner
	winner = True
	for nominee in nominees:
		nominee_link = 'http://en.wikipedia.org{}'.format(nominee.attrib['href'])
		nominee_page = requests.get(nominee_link)
		# winner_page.url gives the requested URL
		parser = etree.HTMLParser()
		nominee_root = etree.fromstring(nominee_page.content, parser)
		# approach: note that each page has a box with a unique class, and the budget / box is in a th with coresponding td
		budget = nominee_root.xpath("//table[@class='infobox vevent']//tr[th='Budget']/td/text()")
		if not budget:
			budget = ['N/A']
		elif budget[0] == '\n':
			boxOffice = nominee_root.xpath("//table[@class='infobox vevent']//tr[th='Budget']/td/div/ul/li[1]/text()")
		boxOffice = nominee_root.xpath("//table[@class='infobox vevent']//tr[th='Box office']/td/text()")
		if not boxOffice:
			boxOffice = ['N/A']
		elif boxOffice[0] == '\n':
			boxOffice = nominee_root.xpath("//table[@class='infobox vevent']//tr[th='Box office']/td/div/ul/li[1]/text()")

		nomineeList.append((i+1928, 
			ith, nominee.text, winner, 
			format(budget[0]), 
			format(boxOffice[0])))
		winner = False

with open('nominees.csv','w') as results:
	csv_results = csv.writer(results)
	csv_results.writerow(['Year', 'No.', 'Title', 'Winner?', 'USD Budget', 'USD Box Office'])
	for row in nomineeList:
		csv_results.writerow(row)

results.close();

