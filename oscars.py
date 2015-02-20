import requests
from lxml import etree
import csv
import re

winnerNames = []
winnerBudgets = []
winnerBoxes =[]

url = "http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture"
res = requests.get(url)
parser = etree.HTMLParser()
root = etree.fromstring(res.content,parser)

# approach: note that the winners all are colored #FAEB86 with a style tag, and these are the only instances of this color on the page.
winners = root.xpath("//tr[contains(@style,'background:#FAEB86')]/td/i/a")

# -*- coding: utf-8 -*-
year = 1928
years = [year]
for winner in winners:
	year += 1
	years.append(year)
	winnerNames.append(winner.text)
	winner_link = winner.attrib['href']
	winner_link = 'http://en.wikipedia.org{}'.format(winner_link)
	winner_page = requests.get(winner_link)
	# winner_page.url gives the requested URL
	parser = etree.HTMLParser()
	winner_root = etree.fromstring(winner_page.content, parser)
	# approach: note that each page has a box with a unique class, and the budget / box is in a th with coresponding td
	budget = winner_root.xpath("//table[@class='infobox vevent']//tr[th='Budget']/td/text()")
	if budget:
		winnerBudgets.append(budget[0])
	else:
		winnerBudgets.append("N/A")
	# same approach as budget for box office
	boxOffice = winner_root.xpath("//table[@class='infobox vevent']//tr[th='Box office']/td/text()")
	if boxOffice:
		# catch "you can't take it with you", which has 2 rows of box office scores. Right now the code only takes the first one (domestic) - could be improved
		if boxOffice[0] == '\n':
			boxOffice = winner_root.xpath("//table[@class='infobox vevent']//tr[th='Box office']/td/div/ul/li[1]/text()")
		winnerBoxes.append(boxOffice[0])
	else:
		winnerBoxes.append("N/A")

# format all of the lists in USD, and calculate the average
def format(string):
	if string != 'N/A':
		formattedString = string.replace(',', '')
		formattedString = re.search(r"[-+]?\d*\.*\d+",formattedString).group()
		formattedString = float(formattedString)
		if 'mil' in string:
			formattedString *= 1000000
		elif 'bil' in string:
			formattedString *= 1000000000
		# catch numbers in GBP
		if u'\xa3' in string:
			return formattedString*1.57
		else:
			return formattedString

# declare formatted arrays, and compute averages
formattedBudgets, formattedBoxes = [], []
budgetTotal, boxOfficeTotal = 0, 0
budgetCount, boxOfficeCount = 0, 0

for i in winnerBudgets:
	formattedBudgets.append(format(i))
	if format(i):
		budgetTotal += format(i)
		budgetCount += 1
for i in winnerBoxes:
	formattedBoxes.append(format(i))
	if format(i):
		boxOfficeTotal += format(i)
		boxOfficeCount += 1
budgetAvg = budgetTotal/float(budgetCount)
boxOfficeAvg = boxOfficeTotal/float(boxOfficeCount)

# create master list of what to output, and output to CSV
years = map(str, years)
master_list = zip(years, winnerNames, winnerBudgets, winnerBoxes, map(str, formattedBudgets), map(str, formattedBoxes))

with open('results.csv','w') as results:
	csv_results = csv.writer(results)
	csv_results.writerow(['Average movie budget:', budgetAvg])
	csv_results.writerow(['Average box office:', boxOfficeAvg])
	csv_results.writerow(['Year','Winning Film','Budget','Box Office', 'Formatted Budget', 'Formatted Box Office'])
	for row in master_list:
		csv_results.writerow([s.encode("utf-8") for s in row])

results.close();

