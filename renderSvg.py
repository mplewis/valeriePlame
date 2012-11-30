#!/usr/bin/python

import pygal
import cPickle
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
firstUsefulTime = cfg['svg']['firstUsefulTime']
customChartList = cfg['svg']['chartsToRender']

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

def getUsefulSortedKeys(unorderedDict):
	sortedKeys = sorted(unorderedDict.keys())
	def isUsefulData(key):
		key = int(key)
		return key > firstUsefulTime
	usefulKeys = filter(isUsefulData, sortedKeys)
	return usefulKeys

def renderAllSvgFromMostRecentData(printProgress = False):

	freshDataLoc = fileUtils.getMostRecentFile()

	if printProgress:
		print('Rendering subject SVGs from ' + freshDataLoc + '...')

	with open(freshDataLoc, 'r') as dataFile:
		courseDict = cPickle.load(dataFile)

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
		if printProgress:
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

def renderTimeSvgFromDiffData(printProgress = False):
	diffData = fileUtils.unpickle(openClosedProcessedFileLoc)
	usefulKeys = getUsefulSortedKeys(diffData)
	columns = diffData[diffData.keys()[0]].keys()
	def isDiffColumn(colName):
		return colName.endswith('Diff')
	diffColumns = filter(isDiffColumn, columns)
	for column in diffColumns:
		if printProgress:
			dynPrint('\tRendering ' + column + '...')
		chartOutLoc = svgDir + '/' + column + '.svg'
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
		chart.render_to_file(chartOutLoc)

def renderCustomCharts(printProgress = False):
	diffData = fileUtils.unpickle(openClosedProcessedFileLoc)
	for chartData in customChartList:
		chartOutLoc = svgDir + '/' + chartData['fileName'] + '.svg'
		if printProgress:
			dynPrint('Rendering ' + chartOutLoc + '...')
		chartTitle = chartData['chartTitle']
		dataTitle = chartData['seriesTitle']
		dataColumn = chartData['column']
		dataMult = chartData['dataMult']
		usefulKeys = getUsefulSortedKeys(diffData)
		chart = pygal.Line(fill = True)
		chart.title = chartTitle + ' (' + season + ' ' + year + ')'
		colData = []
		prettyTimeDict = {}
		for key in usefulKeys:
			dataPoint = {}
			dateItem = diffData[key]
			data = dateItem[dataColumn] * dataMult
			prettyTime = datetime.datetime.fromtimestamp(int(key)).strftime('%m/%d %H:%M')
			prettyTimeDict[key] = prettyTime
			prettyInterval = \
				datetime.datetime.fromtimestamp(int(key) - 1800).strftime('%m/%d: %H:%M') + ' to ' + \
				datetime.datetime.fromtimestamp(int(key)).strftime('%H:%M')
			dataPoint['value'] = data
			dataPoint['label'] = prettyInterval
			colData.append(dataPoint)
		prettyTimeLabels = []
		keyCount = 0
		for timeKey in usefulKeys[:]:
			# this is a magic equation that tells us whether a unixtime is from 0 to 5 minutes past 8am
			if ((int(timeKey) + 3600 * 10) % 86400) < 300:
				prettyTimeLabels.append(datetime.datetime.fromtimestamp(int(timeKey)).strftime('%m/%d 8am'))
			else:
				prettyTimeLabels.append('')
		chart.x_labels = prettyTimeLabels
		chart.add(dataTitle, colData)
		chart.render_to_file(chartOutLoc)
	if printProgress:
		dynPrint('Done.')


if __name__ == '__main__':
	renderCustomCharts(printProgress = True)
	dynPrint('Done. Custom SVGs rendered to ' + svgDir + '/.\n')