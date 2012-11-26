import json
import fileUtils
from loadConfig import loadConfig

cfg = loadConfig()
statsOutputDir = cfg['dataLoc']['statsDir']
statsExt = cfg['dataLoc']['statsFiles']['statsExt']
openClosedProcessedFileName = cfg['dataLoc']['statsFiles']['openClosedData']['processed'] + '.' + statsExt
openClosedProcessedFileLoc = statsOutputDir + '/' + openClosedProcessedFileName
statsOutputDir = cfg['dataLoc']['statsDir']
jsonFullOutLoc = cfg['dataLoc']['statsDir'] + '/' + 'webData.json'

diffData = fileUtils.unpickle(openClosedProcessedFileLoc)

jsonData = []

for key in sorted(diffData[diffData.keys()[0]]):
	print key

sortedKeys = sorted(diffData.keys())[1:]

for key in sortedKeys:
	print key

for dateKey in sortedKeys:
	jsDate = int(dateKey) * 1000
	data = diffData[dateKey]['numSeatsOpenDelta']
	print jsDate
	jsonData.append([jsDate, data])

print json.dumps(jsonData)