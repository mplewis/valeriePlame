import csv
import pickle
import mathUtils
from loadConfig import loadConfig

cfg = loadConfig()

statsOutputDir = cfg['dataLoc']['statsDir']

statsExt = cfg['dataLoc']['statsFiles']['statsExt']

openClosedRawFileName = cfg['dataLoc']['statsFiles']['openClosedData']['raw'] + '.' + statsExt
openClosedRawFileLoc = statsOutputDir + '/' + openClosedRawFileName

openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName

sanityCheckColumn = cfg['stats']['sanityCheckColumn']
sanityPercent = cfg['stats']['sanityCheckPercent']

def processRawData():
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
	print 'Processing raw data from ' + openClosedRawFileLoc + '...'
	processRawData()
	print 'Done. Raw data processed into ' + openClosedProcessedFileLoc + '.'