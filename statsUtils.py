#!/usr/bin/python

import yaml
import fileUtils
import mathUtils
import cPickle
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

subjectSeatsFileLoc = statsOutputDir + '/' + 'subjectSeats.dat'

subjListFileLoc = cfg['dataLoc']['subjList']

sanityCheckColumn = cfg['stats']['sanityCheckColumn']
sanityPercent = cfg['stats']['sanityCheckPercent']

undergradCoursesOnly = cfg['oneStop']['undergradCoursesOnly']
maxCourseLevel = cfg['oneStop']['maxUndergradLevel']

def getOpenClosedStats(courseDict):
	columns = ['numCoursesTotal', 'numCoursesAllSectionsClosed', 'numCoursesSomeSectionsOpen', 'numCoursesAllSectionsOpen', 'numSectionsTotal', 'numSectionsClosed', 'numSectionsOpen', 'numSeatsTotal', 'numSeatsFilled', 'numSeatsOpen']
	stats = {}
	for column in columns:
		stats[column] = 0
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

def processScrapedToOpenClosed(printProgress = False):
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
			existingData = cPickle.load(existingDataFile)
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
		print 'Processing open/closed data:', numFilesTotal, pluralText, 'to analyze.'
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
			courseDataRaw = fileUtils.unpickle(fileToAnalyze)
			courseDataProc = getOpenClosedStats(courseDataRaw)
			allData[fileTime] = courseDataProc
			numFilesProcessed += 1
		with open(openClosedRawFileLoc, 'w') as dataOut:
			cPickle.dump(allData, dataOut)

# sanity check: remove outliers from the data set
def sanityCheck(openClosedData):
	# get the median of the number of total sections from the data set and store it in saneMedian
	sanityMedianData = []
	for key in openClosedData:
		sanityMedianData.append(openClosedData[key][sanityCheckColumn])

	saneMedian = mathUtils.getListMedian(sanityMedianData)

	# if a key's number of total sections isn't within sanityPercent of the median value,
	#    remove it from the list of values to write
	for key in openClosedData.keys():
		sanityTestVal = openClosedData[key][sanityCheckColumn]
		if not mathUtils.withinPercent(sanityPercent, saneMedian, sanityTestVal):
			del openClosedData[key]

	# sort dict keys into sortedKeys and return
	sortedKeys = openClosedData.keys()
	sortedKeys.sort()
	return sortedKeys

def processOpenClosedToDiff():
	# load and unpickle.stats open/closed data dict
	with open(openClosedRawFileLoc, 'r') as dataIn:
		openClosed = cPickle.load(dataIn)

	sortedKeys = sanityCheck(openClosed)

	# generate diff data for every column
	for dateKey in sortedKeys:
		dataItem = openClosed[dateKey]

		# can't generate diff data for the first data point,
		#     so only get diff data for every other point
		if not dateKey == sortedKeys[0]:
			currKeyIndex = sortedKeys.index(dateKey)
			prevKeyIndex = currKeyIndex - 1
			prevKey = sortedKeys[prevKeyIndex]
			prevDataItem = openClosed[prevKey]
			for colKey in dataItem.keys()[:]:
				colKeyDiff = colKey + 'Diff'
				colValDiff = dataItem[colKey] - prevDataItem[colKey]
				dataItem[colKeyDiff] = colValDiff

			# generate diff data for seats open, adjusted for seats that the University adds or removes
			dataItem['numSeatsOpenDelta'] = dataItem['numSeatsOpenDiff'] - dataItem['numSeatsTotalDiff']

	with open(openClosedProcessedFileLoc, 'w') as processedDictOut:
		cPickle.dump(openClosed, processedDictOut)

def getSubjSeatStats(subjList, subjDataRaw):
	columns = ['numSeatsOpen', 'numSeatsTotal']
	subjDataProc = {}
	for subj in subjList:
		subjDataProc[subj] = {}
		for column in columns:
			subjDataProc[subj][column] = 0
	for courseKey in subjDataRaw:
		course = subjDataRaw[courseKey]
		courseSubj = course.getCourseSubj()
		sectionsDict = course.getAllSections()
		for sectionKey in sectionsDict:
			section = sectionsDict[sectionKey]
			seatsOpen = section.getSeatsOpen()
			seatsTotal = section.getSeatsTotal()
			subjDataProc['****']['numSeatsOpen'] += seatsOpen
			subjDataProc['****']['numSeatsTotal'] += seatsTotal
			subjDataProc[courseSubj]['numSeatsOpen'] += seatsOpen
			subjDataProc[courseSubj]['numSeatsTotal'] += seatsTotal
	return subjDataProc

def processScrapedToSubjectSeats(printProgress = False):
	subjDict = fileUtils.unpickle(subjListFileLoc)
	subjList = sorted(subjDict.keys())
	filesToAnalyze = fileUtils.getAllFiles(dataDir = courseDataDir, dataExt = courseDataExt, latestFirst = False)
	try:
		with open(subjectSeatsFileLoc, 'r') as existingDataFile:
			allData = cPickle.load(existingDataFile)
	except IOError:
		allData = {'_filesProcessed': set()}
	numFilesProcessed = 0
	numFilesTotal = len(filesToAnalyze)
	pluralText = 'files'
	if numFilesTotal == 1:
		pluralText = 'file'
	if numFilesTotal > 0:
		openClosedData = fileUtils.unpickle(openClosedRawFileLoc)
		saneOpenClosedFileKeys = sanityCheck(openClosedData)
		saneOpenClosedFileKeysSet = set(saneOpenClosedFileKeys)
		saneFileKeys = saneOpenClosedFileKeysSet.intersect(set(fileUtils.getAllFiles()))
		existingFileKeys = allData['_filesProcessed']
		unprocessedFileKeysSet = set(saneFileKeys).difference(existingFileKeys)
		print len(unprocessedFileKeysSet), 'unprocessed files'
		unprocessedFileKeys = sorted(list(unprocessedFileKeysSet))
		#print unprocessedFileKeys
		for fileTime in unprocessedFileKeys:
			fileLoc = courseDataDir + '/' + fileTime + '.' + courseDataExt
			print fileLoc
			# FIXME This is super hackish and you should fix it, Matt
			try:
				subjDataRaw = fileUtils.unpickle(fileLoc)
			except IOError:
				continue # with the next file if the one being opened doesn't exist
			subjDataProc = getSubjSeatStats(subjList, subjDataRaw)
			allData[fileTime] = subjDataProc
			allData['_filesProcessed'].add(fileTime)
			numFilesProcessed += 1
		with open(subjectSeatsFileLoc, 'w') as dataOut:
			cPickle.dump(allData, dataOut)

if __name__ == '__main__':
	processScrapedToOpenClosed(printProgress = True)
	dynPrint('Done. Adding diff data to open/closed data...\n')
	processOpenClosedToDiff()
	print 'Done. Processing raw data to section data...'
	processScrapedToSubjectSeats(printProgress = True)