import csv
import pickle
import datetime
import mathUtils
from loadConfig import loadConfig

cfg = loadConfig()
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName
csvFullOutLoc = cfg['dataLoc']['statsDir'] + '/' + cfg['dataLoc']['csvDir'] + '.csv'

def writeFullCsv():
	# open processed data
	with open(openClosedProcessedFileLoc, 'r') as processedDictIn:
		stats = pickle.load(processedDictIn)

	# make a CSV column list from existing columns in stats dict
	# get a list of columns from any (since order is indeterminate) key in the dict,
	#     then sort the list of columns alphabetically
	anyKey = stats.keys()[0]
	columns = stats[anyKey].keys()
	columns.sort()
	# prepend a time column
	columns.insert(0, 'time')

	# sort dict keys into sortedKeys
	sortedKeys = stats.keys()
	sortedKeys.sort()

	# write data to a CSV file using the csv library
	with open(csvFullOutLoc, 'w') as csvOut:
		writer = csv.DictWriter(csvOut, columns, restval = '0')
		writer.writeheader()

		for dateKey in sortedKeys:
			dataItem = stats[dateKey]
			unixTime = dateKey
			prettyTime = datetime.datetime.fromtimestamp(int(unixTime)).strftime('%m/%d/%Y %H:%M:%S')
			dataItem['time'] = prettyTime
			writer.writerow(dataItem)

def writeWebCsv():
	pass

if __name__ == '__main__':
	print 'Processing data from ' + openClosedProcessedFileLoc + '...'
	writeFullCsv()
	print 'Done. CSV written to ' + csvFullOutLoc + '.'