#!/usr/bin/python

import json
import fileUtils
from loadConfig import loadConfig

cfg = loadConfig()
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName
jsonFullOutLoc = cfg['dataLoc']['stockJson']
firstUsefulTime = cfg['stockChart']['firstUsefulTime']
dataColumn = cfg['stockChart']['column']
dataMult = cfg['stockChart']['dataMult']

diffData = fileUtils.unpickle(openClosedProcessedFileLoc)

jsonData = []

def getUsefulSortedKeys(unorderedDict):
	sortedKeys = sorted(unorderedDict.keys())
	def isUsefulData(key):
		key = int(key)
		return key > firstUsefulTime
	usefulKeys = filter(isUsefulData, sortedKeys)
	return usefulKeys

usefulKeys = getUsefulSortedKeys(diffData)[1:]

for dateKey in usefulKeys:
	# move everything back 6 hours from GMT so the times match up to 8am on registratio days,
	#     then move everything back a half hour so that 8am shows the registrations after it, not before it
	jsDate = (int(dateKey) - (6 * 3600) - (3600 / 2)) * 1000
	data = diffData[dateKey]['numSeatsOpenDelta'] * dataMult
	jsonData.append([jsDate, data])

with open(jsonFullOutLoc, 'w') as jsonOut:
	json.dump(jsonData, jsonOut)