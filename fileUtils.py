import glob
from loadConfig import loadConfig

cfg = loadConfig()
dataDir = cfg['dataLoc']['courseDataDir']
dataExt = cfg['dataLoc']['courseDataExt']

def getMostRecentFile():
	directory = "oneStopData"
	extension = "dat"
	files = glob.glob(directory + '/' + '*.' + extension)
	files.sort(reverse = True)
	return files[0]

if __name__ == '__main__':
	print 'Most recent datafile:', getMostRecentFile()