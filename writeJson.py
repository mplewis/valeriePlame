#!/usr/bin/python

import json
import fileUtils
from loadConfig import loadConfig

cfg = loadConfig()
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName
jsonFullOutLoc = cfg['dataLoc']['json']['seatsAllSubjs']
jsonDividedOutLoc = cfg['dataLoc']['json']['seatsBySubj']
firstUsefulTime = cfg['stockChart']['firstUsefulTime']
dataColumn = cfg['stockChart']['column']
dataMult = cfg['stockChart']['dataMult']
subjectDataLoc = cfg['dataLoc']['subjList']
subjectSeatsFileLoc = statsOutputDir + '/' + 'subjectSeats.dat'

if __name__ == '__main__':
	diffData = fileUtils.unpickle(openClosedProcessedFileLoc)
	subjSeatsData = fileUtils.unpickle(subjectSeatsFileLoc)
	del subjSeatsData['_filesProcessed']

	# print subjSeatsData

	subjectDict = fileUtils.unpickle(subjectDataLoc)
	subjects = sorted(subjectDict.keys())

	jsonFullData = []
	jsonSubjData = []

	def getUsefulSortedKeys(unorderedDict):
		sortedKeys = sorted(unorderedDict.keys())
		def isUsefulData(key):
			key = int(key)
			return key > firstUsefulTime
		usefulKeys = filter(isUsefulData, sortedKeys)
		return usefulKeys

	usefulFullKeys = getUsefulSortedKeys(diffData)[1:]

	for dateKey in usefulFullKeys:
		# move everything back 6 hours from GMT so the times match up to 8am on registration days,
		#     then move everything back a half hour so that 8am shows the registrations after it, not before it
		jsDate = (int(dateKey) - (6 * 3600) - (3600 / 2)) * 1000
		data = diffData[dateKey]['numSeatsOpenDelta'] * dataMult
		jsonFullData.append([jsDate, data])

	usefulSubjKeys = getUsefulSortedKeys(subjSeatsData)

	for dateKey in usefulSubjKeys:
		#for subj in subjects:
		for subj in ['CSCI']:
			dataPoint = subjSeatsData[dateKey]
			if not subj in dataPoint:
				print dateKey, subj, 'not found in', dateKey
			else:
				print dateKey, subj, dataPoint[subj]

	with open(jsonFullOutLoc, 'w') as jsonOut:
		json.dump(jsonFullData, jsonOut)