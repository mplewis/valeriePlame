#!/usr/bin/python

import cPickle
from loadConfig import loadConfig

cfg = loadConfig()
subjListLoc = cfg['dataLoc']['subjList']

with open(subjListLoc, 'r') as subjData:
	subjList = cPickle.load(subjData)

def getFullSubjFromAbbr(subjAbbr):
	return subjList[subjAbbr]

# season: 'fall', 'spring', 'summer'
# year: 2012, 2013, ...
# subjAbbr: 'CSCI', 'ECON', 'ARTS', ...
def getOneStopSearchUrl(season, year, subjAbbr):
	seasonClean = season.strip().capitalize()
	if seasonClean != 'Fall' and seasonClean != 'Spring' and seasonClean != 'Summer':
		raise LookupError(season + " is not a valid season. Valid seasons are: 'Fall', 'Spring', 'Summer'")
	try:
		# ensure year is a number, then make it a string again
		yearClean = int(year)
		yearClean = str(yearClean)
	except ValueError:
		raise ValueError('Not a valid year: ' + year)
	subjNameFull = getFullSubjFromAbbr(subjAbbr).replace(' ', '%20')
	# Fall 2012: 1129, Spring 2013: 1133, Summer 2013: 1135
	if seasonClean == 'Fall' and yearClean == '2012':
		magicNum = '1129'
	elif seasonClean == 'Spring' and yearClean == '2013':
		magicNum = '1133'
	elif seasonClean == 'Summer' and yearClean == '2013':
		magicNum = '1135'
	else:
		print repr(seasonClean), repr(yearClean)
		raise LookupError('Not a valid year/season combination: ' + seasonClean + ', ' + yearClean)
	url = 'http://onestop2.umn.edu/courseinfo/viewSearchResults.do?campus=UMNTC&swapNow=N&searchTerm=UMNTC%2C' + magicNum + '%2C' + seasonClean + '%2C' + yearClean + '&searchSubjects=' + subjNameFull + '&searchCatalogNumber=&searchClassroom=true&searchOpenSections=false&searchLowerStartTime=00%3A00%2C12%3A00&searchUpperEndTime=23%3A59%2C11%3A59&searchMon=true&searchTue=true&searchWed=true&searchThu=true&searchFri=true&searchSat=true&searchSun=true&searchLowerLevelLimit=0%2C0xxx&searchUpperLevelLimit=9999%2C9xxx&searchLowerCreditLimit=0&searchUpperCreditLimit=9999&searchInstructorName=&searchCourseTitle=&searchSessionCodes=ALL%2CALL&searchLocations=TCEASTBANK%2CEast+Bank&searchLocations=TCWESTBANK%2CWest+Bank&searchLocations=STPAUL%2CSt.+Paul&campus=UMNTC&search=Search'
	return url

# test cases; show that getting a full subject from an abbreviation works and
#     that getting a search url from a subject works too
if __name__ == '__main__':
	print getFullSubjFromAbbr('csci')
	print getFullSubjFromAbbr('Math')
	print getFullSubjFromAbbr('ARTS')
	print getOneStopSearchUrl('Fall', '2012', 'Ee')
	print getOneStopSearchUrl('Summer', '2013', '****')