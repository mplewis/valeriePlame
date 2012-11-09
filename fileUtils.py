import glob
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

if __name__ == '__main__':
	print 'Most recent datafile:', getMostRecentFile()