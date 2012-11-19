#!/usr/bin/python

import pygal
import pickle
import oneStopUtils
import fileUtils
import datetime
from loadConfig import loadConfig
from umnCourseObj import UmnCourse, UmnSection
from dynPrint import dynPrint

cfg = loadConfig()
season = cfg['oneStop']['season']
year = str(cfg['oneStop']['year'])
svgDir = cfg['dataLoc']['svgDir']
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName

# modified default Pygal style
customChartStyle = pygal.style.Style( \
	opacity = '.4',
	opacity_hover = '.75',
	transition = '.25s ease-out',
	background = '#7c111a',
	plot_background = 'transparent',
	foreground = '#dcc', # legend text
	foreground_light = '#fff', # title text
	# unused: foreground_dark = '#00f',
	# red, yellow, green
	colors = ('#e95355', '#feed6c', '#b6e354')
)

def initDictKey(dic, key):
	if not key in dic:
		dic[key] = 0

def incrDictKey(dic, key):
	if key in dic:
		dic[key] += 1
	else:
		dic[key] = 1

def getPluralStr(num, string):
	if num == 1:
		return string
	else:
		return string + 's'

def renderAllSvgFromMostRecentData(printStatus = True):
	dynPrint('\tScraping data...')

	freshDataLoc = fileUtils.getMostRecentFile()

	with open(freshDataLoc, 'r') as dataFile:
		courseDict = pickle.load(dataFile)

	numUndergrad = 0
	numGraduate = 0
	ugCourseDict = {}
	ugCourseSubjCount = {}
	ugAllSectionsClosed = 0
	ugSomeSectionsOpen = 0
	ugAllSectionsOpen = 0
	ugCourseSubjAllClosedCount = {}
	ugCourseSubjSomeOpenCount = {}
	ugCourseSubjAllOpenCount = {}

	for courseId in courseDict:
		course = courseDict[courseId]
		if course.getCourseLevel() <= 4:
			numUndergrad += 1
			ugCourseDict[courseId] = course
		else:
			numGraduate += 1

	for ugCourseId in ugCourseDict:
		subjAbbr = ugCourseDict[ugCourseId].getCourseSubj()

		incrDictKey(ugCourseSubjCount, subjAbbr)

		if ugCourseDict[ugCourseId].getNumSectionsOpen() == 0:
			ugAllSectionsClosed += 1
			incrDictKey(ugCourseSubjAllClosedCount, subjAbbr)
		elif ugCourseDict[ugCourseId].getNumSectionsClosed() == 0:
			ugAllSectionsOpen += 1
			incrDictKey(ugCourseSubjAllOpenCount, subjAbbr)
		else:
			ugSomeSectionsOpen += 1
			incrDictKey(ugCourseSubjSomeOpenCount, subjAbbr)

	oneStopHomeUrl = 'http://onestop2.umn.edu/courseinfo/searchcriteria.jsp?institution=UMNTC'
	chart = pygal.Pie(
		style = customChartStyle,
		width = 780,
		height = 585
	)
	chart.title = 'Undergrad course availability (' + season + ' ' + year + ')'
	textUgAllClosed = getPluralStr(ugAllSectionsClosed, ' course')
	chart.add('All closed', [{
		'value': ugAllSectionsClosed,
		'label': str(ugAllSectionsClosed) + textUgAllClosed,
		'xlink': oneStopHomeUrl
	}])
	textUgSomeOpen = getPluralStr(ugSomeSectionsOpen, ' course')
	chart.add('Some open', [{
		'value': ugSomeSectionsOpen,
		'label': str(ugSomeSectionsOpen) + textUgSomeOpen,
		'xlink': oneStopHomeUrl
	}])
	textUgAllOpen = getPluralStr(ugAllSectionsOpen, ' course')
	chart.add('All open', [{
		'value': ugAllSectionsOpen,
		'label': str(ugAllSectionsOpen) + textUgAllOpen,
		'xlink': oneStopHomeUrl
	}])
	chart.render_to_file(svgDir + '/' + 'undergrad' + '.svg')

	for subj in ugCourseSubjCount:
		dynPrint('\tRendering ' + subj + '...')
		initDictKey(ugCourseSubjAllClosedCount, subj)
		initDictKey(ugCourseSubjAllOpenCount, subj)
		initDictKey(ugCourseSubjSomeOpenCount, subj)
		
		# style is neon, slightly modified, with different colors
		chart = pygal.Pie(
			style = customChartStyle,
			width = 300,
			height = 225,
			tooltip_font_size = 11,
			legend_font_size = 11,
		)

		searchUrl = oneStopUtils.getOneStopSearchUrl(season, year, subj)
		chart.title = subj + ' (' + season + ' ' + year + ')'
		numAllClosed = ugCourseSubjAllClosedCount[subj]
		textAllClosed = getPluralStr(numAllClosed, ' course')
		chart.add('All closed', [{
			'value': numAllClosed,
			'label': str(numAllClosed) + textAllClosed,
			'xlink': {
				'href': searchUrl,
				'show': 'new'
			}
		}])
		numSomeOpen = ugCourseSubjSomeOpenCount[subj]
		textSomeOpen = getPluralStr(numSomeOpen, ' course')
		chart.add('Some open', [{
			'value': numSomeOpen,
			'label': str(numSomeOpen) + textSomeOpen,
			'xlink': {
				'href': searchUrl,
				'show': 'new'
			}
		}])
		numAllOpen = ugCourseSubjAllOpenCount[subj]
		textAllOpen = getPluralStr(numAllOpen, ' course')
		chart.add('All open', [{
			'value': numAllOpen,
			'label': str(numAllOpen) + textAllOpen,
			'xlink': {
				'href': searchUrl,
				'show': 'new'
			}
		}])
		chart.render_to_file(svgDir + '/' + subj + '.svg')

def renderTimeSvgFromDiffData(printStatus = False):
	with open(openClosedProcessedFileLoc, 'r') as diffFile:
		diffData = pickle.load(diffFile)
	sortedKeys = sorted(diffData.keys())
	def isUsefulData(key):
		key = int(key)
		firstUsefulTime = 1352793600 # everything after this counts
		return key > firstUsefulTime
	usefulKeys = filter(isUsefulData, sortedKeys)
	columns = diffData[diffData.keys()[0]].keys()
	def isDiffColumn(colName):
		return colName.endswith('Diff')
	diffColumns = filter(isDiffColumn, columns)
	for column in diffColumns:
		if printStatus:
			dynPrint('\tRendering ' + column + '...')
		svgOutLoc = svgDir + '/' + column + '.svg'
		chart = pygal.Line(fill = True)
		chart.title = column
		colData = []
		prettyTimeDict = {}
		for key in usefulKeys:
			dateItem = diffData[key]
			colData.append(dateItem[column])
			prettyTime = datetime.datetime.fromtimestamp(int(key)).strftime('%m/%d/%Y %H:%M:%S')
			prettyTimeDict[key] = prettyTime
		chart.add('Data', colData)
		chart.render_to_file(svgOutLoc)

if __name__ == '__main__':
	print 'Rendering subject SVGs from ' + fileUtils.getMostRecentFile() + '...'
	#renderAllSvgFromMostRecentData(printStatus = True)
	dynPrint('Done. Rendering diff SVGs from ' + openClosedProcessedFileLoc + '...\n')
	renderTimeSvgFromDiffData(printStatus = True)
	dynPrint('Done. SVGs saved to ' + svgDir + '/.\n')