#!/usr/bin/python

import yaml
import fileUtils
import mathUtils
import pickle
import time
from loadConfig import loadConfig
from umnCourseObj import UmnCourse, UmnSection
from consoleSize import consoleSize

cfg = loadConfig()

courseDataDir = cfg['dataLoc']['courseDataDir']
courseDataExt = cfg['dataLoc']['courseDataExt']
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']

openClosedRawFileName = cfg['dataLoc']['statsFiles']['openClosedData']['raw'] + '.' + cfg['dataLoc']['statsFiles']['statsExt']
openClosedRawFileLoc = statsOutputDir + '/' + openClosedRawFileName
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName

sanityCheckColumn = cfg['stats']['sanityCheckColumn']
sanityPercent = cfg['stats']['sanityCheckPercent']

undergradCoursesOnly = cfg['oneStop']['undergradCoursesOnly']
maxCourseLevel = cfg['oneStop']['maxUndergradLevel']

class DataAnalyzer:
	def __init__(self, dataFileLoc):
		self.file = dataFileLoc
		self.dataRead = False
		self.data = None
	def refresh(self):
		courses = fileUtils.unpickle(self.file)
		self.data = getUndergradStats(courses)
		self.dataRead = True
	def getData(self):
		if not self.dataRead:
			self.refresh()
		return self.data
	def __repr__(self):
		if not self.dataRead:
			self.refresh()
		fileTime = fileUtils.getFileNameFromPath(self.file)
		return "Data from " + str(fileTime) + ': ' + str(self.data)

def getUndergradStats(courseDict):
	stats = {}
	stats['numCoursesTotal'] = 0
	stats['numCoursesAllSectionsClosed'] = 0
	stats['numCoursesSomeSectionsOpen'] = 0
	stats['numCoursesAllSectionsOpen'] = 0
	stats['numSectionsTotal'] = 0
	stats['numSectionsClosed'] = 0
	stats['numSectionsOpen'] = 0
	stats['numSeatsTotal'] = 0
	stats['numSeatsFilled'] = 0
	stats['numSeatsOpen'] = 0
	for courseKey in courseDict:
		course = courseDict[courseKey]
		if undergradCoursesOnly and course.getCourseLevel() <= maxCourseLevel:
			stats['numSectionsTotal'] += course.getNumSections()
			stats['numSectionsClosed'] += course.getNumSectionsClosed()
			stats['numSectionsOpen'] += course.getNumSectionsOpen()
			stats['numCoursesTotal'] += 1
			if course.getNumSectionsOpen() == 0:
				stats['numCoursesAllSectionsClosed'] += 1
			elif course.getNumSectionsClosed() == 0:
				stats['numCoursesAllSectionsOpen'] += 1
			else:
				stats['numCoursesSomeSectionsOpen'] += 1
			sectionDict = course.getAllSections()
			for sectionKey in sectionDict:
				section = sectionDict[sectionKey]
				stats['numSeatsTotal'] += section.getSeatsTotal()
				stats['numSeatsFilled'] += section.getSeatsFilled()
				stats['numSeatsOpen'] += section.getSeatsOpen()
	return stats

def processScrapedToRaw(printProgress = False):
	from dynPrint import dynPrint

	def statusOut():
		out = str(pctComplete) + '% complete: ' + \
			'File ' + str(numFilesProcessed + 1) + '/' + str(numFilesTotal) + \
			' (' + fileTime + '.' + courseDataExt + ')' + \
			alignRightSpacer + \
			eta
		return out
	filesToAnalyze = fileUtils.getAllFiles(dataDir = courseDataDir, dataExt = courseDataExt, latestFirst = False)
	try:
		with open(openClosedRawFileLoc, 'r') as existingDataFile:
			existingData = pickle.load(existingDataFile)
			fileNamesToAnalyze = [fileUtils.getFileNameFromPath(fileName) for fileName in filesToAnalyze]
			fileNamesToAnalyze = list(set(fileNamesToAnalyze).difference(set(existingData)))
			filesToAnalyze = [courseDataDir + '/' + fileName + '.' + courseDataExt for fileName in fileNamesToAnalyze]
			allData = existingData
	except IOError:
		allData = {}
	numFilesProcessed = 0
	numFilesTotal = len(filesToAnalyze)
	if printProgress:
		print 'Analyzing datafiles:', numFilesTotal, 'files to analyze.'
	if numFilesTotal > 0:
		startTime = time.clock()
		alignRightSpacer = ''
		for fileToAnalyze in filesToAnalyze:
			fileTime = fileUtils.getFileNameFromPath(fileToAnalyze)
			timePassed = time.clock() - startTime
			numfilesLeft = numFilesTotal - numFilesProcessed
			pctComplete = numFilesProcessed * 100 / numFilesTotal
			if numFilesProcessed == 0:
				eta = ''
			else:
				etaTime = (timePassed / numFilesProcessed) * numfilesLeft
				etaTimePretty = time.strftime('%H:%M:%S', time.gmtime(etaTime))
				eta = ' (ETA: ' + etaTimePretty + ')'
			consoleWidth = int(consoleSize()[0])
			while len(statusOut()) != consoleWidth:
				if len(statusOut()) < consoleWidth:
					alignRightSpacer += ' '
				else:
					if len(alignRightSpacer) == 0:
						break
					alignRightSpacer = alignRightSpacer[:-1]
			if printProgress:
				dynPrint(statusOut())
			dRead = DataAnalyzer(fileToAnalyze)
			dRead.refresh()
			allData[fileTime] = dRead.getData()
			numFilesProcessed += 1
		with open(openClosedRawFileLoc, 'w') as dataOut:
			pickle.dump(allData, dataOut)

def processRawToDiff():
	# load and unpickle stats data dict
	with open(openClosedRawFileLoc, 'r') as dataIn:
		stats = pickle.load(dataIn)

	# sanity check: remove outliers from the data set

	# get the median of the number of total sections from the data set and store it in saneMedian
	sanityMedianData = []
	for key in stats:
		sanityMedianData.append(stats[key][sanityCheckColumn])

	saneMedian = mathUtils.getListMedian(sanityMedianData)

	# if a key's number of total sections isn't within sanityPercent of the median value,
	#    remove it from the list of values to write
	for key in stats.keys():
		sanityTestVal = stats[key][sanityCheckColumn]
		if not mathUtils.withinPercent(sanityPercent, saneMedian, sanityTestVal):
			del stats[key]

	# make a CSV column list from existing columns in stats dict

	# get a list of columns from any (since order is indeterminate) key in the dict,
	#     then sort the list of columns alphabetically
	anyKey = stats.keys()[0]
	columns = stats[anyKey].keys()
	columns.sort()
	# add columns with 'Diff' appended to the column list
	for key in columns[:]:
		columns.append(key + 'Diff')
	# prepend a time column
	columns.insert(0, 'time')

	# sort dict keys into sortedKeys
	sortedKeys = stats.keys()
	sortedKeys.sort()

	for dateKey in sortedKeys:
		dataItem = stats[dateKey]

		if not dateKey == sortedKeys[0]:
			currKeyIndex = sortedKeys.index(dateKey)
			prevKeyIndex = currKeyIndex - 1
			prevKey = sortedKeys[prevKeyIndex]
			prevDataItem = stats[prevKey]
			for colKey in dataItem.keys():
				colKeyDiff = colKey + 'Diff'
				colValDiff = dataItem[colKey] - prevDataItem[colKey]
				dataItem[colKeyDiff] = colValDiff

	with open(openClosedProcessedFileLoc, 'w') as processedDictOut:
		pickle.dump(stats, processedDictOut)

if __name__ == '__main__':
	processScrapedToRaw(printProgress = True)
	print 'Processing raw data from ' + openClosedRawFileLoc + '...'
	processRawToDiff()
	print 'Done. Raw data processed into ' + openClosedProcessedFileLoc + '.'