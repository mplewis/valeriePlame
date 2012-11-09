import glob
from loadConfig import loadConfig

cfg = loadConfig()
dataDir = cfg['dataLoc']['courseDataDir']
dataExt = cfg['dataLoc']['courseDataExt']

def getMostRecentFile():
	return getAllFiles(latestFirst = True)[0]

def getAllFiles(latestFirst = True):
	directory = dataDir
	extension = dataExt
	files = glob.glob(directory + '/' + '*.' + extension)
	files.sort(reverse = latestFirst)
	return files

if __name__ == '__main__':
	print 'Most recent datafile:', getMostRecentFile()