#!/usr/bin/python

import yaml
import fileUtils
import pickle
from dynPrint import dynPrint
from loadConfig import loadConfig
from umnCourseObj import UmnCourse, UmnSection

cfg = loadConfig()
courseDataDir = cfg['dataLoc']['courseDataDir']
courseDataExt = cfg['dataLoc']['courseDataExt']
statsOutputDir = cfg['dataLoc']['statsDir']

openClosedFileName = cfg['dataLoc']['statsFiles']['openClosedData'] + '.' + cfg['dataLoc']['statsFiles']['statsExt']
openClosedFileLoc = statsOutputDir + '/' + openClosedFileName

cfgMaxCourseLevel = cfg['oneStop']['maxUndergradLevel']

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
		if course.getCourseLevel() <= cfgMaxCourseLevel:
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

if __name__ == '__main__':
	filesToAnalyze = fileUtils.getAllFiles(dataDir = courseDataDir, dataExt = courseDataExt, latestFirst = False)
	try:
		with open(openClosedFileLoc, 'r') as existingDataFile:
			existingData = pickle.load(existingDataFile)
			fileNamesToAnalyze = [fileUtils.getFileNameFromPath(fileName) for fileName in filesToAnalyze]
			fileNamesToAnalyze = list(set(fileNamesToAnalyze).difference(set(existingData)))
			filesToAnalyze = [courseDataDir + '/' + fileName + '.' + courseDataExt for fileName in fileNamesToAnalyze]
			allData = existingData
	except IOError:
		allData = {}
	numFilesProcessed = 0
	numFilesTotal = len(filesToAnalyze)
	print numFilesTotal, 'datafiles to analyze.'
	for fileToAnalyze in filesToAnalyze:
		numFilesProcessed += 1
		fileTime = fileUtils.getFileNameFromPath(fileToAnalyze)
		dynPrint('Datafile ' + str(numFilesProcessed) + ' of ' + str(numFilesTotal) + ' (' + str(fileTime) + ')')
		dRead = DataAnalyzer(fileToAnalyze)
		dRead.refresh()
		allData[fileTime] = dRead.getData()
	with open(openClosedFileLoc, 'w') as dataOut:
		pickle.dump(allData, dataOut)
	print '\nDone. Data stored to ' + openClosedFileLoc + '.'