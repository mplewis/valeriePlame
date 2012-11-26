#!/usr/bin/python

import yaml
import fileUtils
import mathUtils
import pickle
import time
from loadConfig import loadConfig
from umnCourseObj import UmnCourse, UmnSection
from consoleSize import consoleSize
from dynPrint import dynPrint

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
	pluralText = 'files'
	if numFilesTotal == 1:
		pluralText = 'file'
	if printProgress:
		print 'Analyzing datafiles:', numFilesTotal, pluralText, 'to analyze.'
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
			try:
				consoleWidth = int(consoleSize()[0])
			except ValueError:
				consoleWidth = 80
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
	# load and unpickle stats raw data dict
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

	# sort dict keys into sortedKeys
	sortedKeys = stats.keys()
	sortedKeys.sort()

	# generate diff data for every column
	for dateKey in sortedKeys:
		dataItem = stats[dateKey]

		# can't generate diff data for the first data point,
		#     so only get diff data for every other point
		if not dateKey == sortedKeys[0]:
			currKeyIndex = sortedKeys.index(dateKey)
			prevKeyIndex = currKeyIndex - 1
			prevKey = sortedKeys[prevKeyIndex]
			prevDataItem = stats[prevKey]
			for colKey in dataItem.keys()[:]:
				colKeyDiff = colKey + 'Diff'
				colValDiff = dataItem[colKey] - prevDataItem[colKey]
				dataItem[colKeyDiff] = colValDiff

			# generate diff data for seats open, adjusted for seats that the University adds or removes
			dataItem['numSeatsOpenDelta'] = dataItem['numSeatsOpenDiff'] - dataItem['numSeatsTotalDiff']

	with open(openClosedProcessedFileLoc, 'w') as processedDictOut:
		pickle.dump(stats, processedDictOut)

if __name__ == '__main__':
	processScrapedToRaw(printProgress = True)
	dynPrint('Done. Processing raw data from ' + openClosedRawFileLoc + '...\n')
	processRawToDiff()
	print 'Done. Raw data processed into ' + openClosedProcessedFileLoc + '.'