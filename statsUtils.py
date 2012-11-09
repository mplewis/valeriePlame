import yaml
import fileUtils
import pickle
from loadConfig import loadConfig
from umnCourseObj import UmnCourse, UmnSection

cfg = loadConfig()
courseDataDir = cfg['dataLoc']['courseDataDir']
courseDataExt = cfg['dataLoc']['courseDataExt']
statsOutputDir = cfg['dataLoc']['statsDir']

class DataAnalyzer:
	def __init__(self, dataFileList):
		self.fileList = dataFileList
	def undergradStatsPrintTest(self):
		for dataFileLoc in self.fileList:
			courses = fileUtils.unpickle(dataFileLoc)
			stats = getUndergradStats(courses)
			fileTime = fileUtils.getFileNameFromPath(dataFileLoc)
			print fileTime, stats

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
		if course.getCourseLevel() <= 4:
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
	print 'Datafiles to analyze (oldest first):'
	for filePath in filesToAnalyze:
		print '\t' + filePath
	stats = DataAnalyzer(filesToAnalyze)
	stats.undergradStatsPrintTest()