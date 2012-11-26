import json
import fileUtils
from loadConfig import loadConfig

cfg = loadConfig()
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName
jsonFullOutLoc = cfg['stockChart']['dataOutLoc']
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
	jsDate = (int(dateKey) - (6 * 3600)) * 1000
	data = diffData[dateKey]['numSeatsOpenDelta'] * dataMult
	jsonData.append([jsDate, data])

with open(jsonFullOutLoc, 'w') as jsonOut:
	json.dump(jsonData, jsonOut)