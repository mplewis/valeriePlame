import urllib2
import oneStopUtils
import string
import time
import pickle
from loadConfig import loadConfig
from unixTime import unixTime
from bs4 import BeautifulSoup, SoupStrainer
from umnCourseObj import UmnCourse, UmnSection

# takes in a tag
# returns tag text without all the crazy whitespace
def cleanTagText(dirtyTag):
	return string.join(dirtyTag.get_text().strip().split())

only_h3 = SoupStrainer('h3')

def bsParseHtml(rawHtml):
	oneStop = BeautifulSoup(rawHtml, 'lxml', parse_only = only_h3)

	courseDict = {}

	# h3.courseTitle indicates the start of a new course
	for h3 in oneStop.find_all('h3'):
		if h3.has_key('class') and h3['class'] == ['courseTitle']:
			courseTitle = cleanTagText(h3)
			courseTitleSplit = courseTitle.split()
			courseSubj = courseTitleSplit[0]
			sectionNum = courseTitleSplit[1]
			courseDesc = string.join(courseTitleSplit[2:])
			course = UmnCourse(courseSubj, sectionNum, courseDesc)
			# table.sectionTable holds info on all sections as child tags
			for sibl in h3.find_next_siblings('table'):
				if sibl.has_key('class') and sibl['class'] == ['sectionTable']:
					sectionTable = sibl
					for td in sectionTable.find_all('td'):
						# td.classNumber contains a section's 5-digit number
						if td.has_key('class') and td['class'] == ['classNumber']:
							sectionNum = cleanTagText(td)
							if sectionNum == "":
								continue
							else:
								section = UmnSection(sectionNum)
								# the next sibling of td.classNumber is td.description,
								# which holds info on the section
								tddesc = td.find_next_sibling()
								for span in tddesc.find_all('span'):
									# span.green either holds "x of y seats open" or
									# "Waitlist becomes available when class fills."
									if span.has_key('class'):
										if span['class'] == ['green']:
											seatsText = cleanTagText(span)
											# "x of y seats open" parses to seatsOpen, seatsTotal,
											# then stores in UmnSection object
											if seatsText.endswith('seats open'):
												seatsTextSplit = seatsText.split()
												seatsOpen = seatsTextSplit[0]
												seatsTotal = seatsTextSplit[2]
												section.setSeatsOpen(seatsOpen)
												section.setSeatsTotal(seatsTotal)
											# waitlist unavailable text
											elif seatsText == 'Waitlist becomes available when class fills.':
												section.setWaitlistNotYetOpen()
										# span.closed holds "Section Closed"
										elif span['class'] == ['closed']:
											section.setSectionClosed()
								for img in tddesc.find_all('img'):
									if img.has_key('src') and img['src'] == 'images/red_waitlistClosed.gif':
										section.setWaitlistClosed()
									elif img.has_key('src') and img['src'] == 'images/green_waitlist.gif':
										section.setWaitlistOpen()
								course.addSection(sectionNum, section)
			courseDict[course.getCourseId()] = course

	return courseDict

def saveCourseDict():
	startTime = time.clock()
	cfg = loadConfig()
	season = cfg['oneStop']['season']
	year = cfg['oneStop']['year']
	courseDataDir = cfg['dataLoc']['courseDataDir']
	dataExt = cfg['dataLoc']['courseDataExt']

	# **** is the abbreviation for 'all subjects'
	oneStopLookupUrl = oneStopUtils.getOneStopSearchUrl(season, year, '****')

	timeScraped = unixTime()

	# retrieve html from OneStop
	htmlObj = urllib2.urlopen(oneStopLookupUrl)
	rawHtml = htmlObj.read()

	courseDict = bsParseHtml(rawHtml)

	with open(courseDataDir + '/' + str(timeScraped) + '.' + dataExt, 'w') as dataOut:
		pickle.dump(courseDict, dataOut)

	totalTime = time.clock() - startTime
	return totalTime

if __name__ == '__main__':
	print 'Scraping OneStop...'
	timeTaken = saveCourseDict()
	print 'Done in', timeTaken, 'seconds.'