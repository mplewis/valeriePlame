import glob
import pickle
from loadConfig import loadConfig

cfg = loadConfig()
defaultDataDir = cfg['dataLoc']['courseDataDir']
defaultDataExt = cfg['dataLoc']['courseDataExt']

def getMostRecentFile():
	return getAllFiles(latestFirst = True)[0]

def getAllFiles(dataDir = defaultDataDir, dataExt = defaultDataExt, latestFirst = True):
	files = glob.glob(dataDir + '/*.' + dataExt)
	files.sort(reverse = latestFirst)
	return files

def getFileNameAndExtFromPath(filePath):
	split = filePath.split('/')
	fileName = split[len(split) - 1]
	fileNameSplit = fileName.split('.')
	return fileNameSplit

def getFileNameFromPath(filePath):
	return getFileNameAndExtFromPath(filePath)[0]

def getFileExtFromPath(filePath):
	return getFileNameAndExtFromPath(filePath)[1]

def unpickle(fileLoc):
	with open(fileLoc, 'r') as dataFile:
		return pickle.load(dataFile)

if __name__ == '__main__':
	mostRecentDataFile = getMostRecentFile()
	print 'Most recent datafile:', mostRecentDataFile
	print 'Name:', getFileNameFromPath(mostRecentDataFile)
	print 'Extension:', getFileExtFromPath(mostRecentDataFile)