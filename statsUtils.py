import yaml
import fileUtils
from loadConfig import loadConfig

cfg = loadConfig()
courseDataDir = cfg['dataLoc']['courseDataDir']
courseDataExt = cfg['dataLoc']['courseDataExt']

class DataAnalyzer:
	def __init__(self, fileList):
		self.fileList = fileList

if __name__ == '__main__':
	filesToAnalyze = fileUtils.getAllFiles(dataDir = courseDataDir, dataExt = courseDataExt, latestFirst = False)
	print 'Datafiles to analyze (oldest first):'
	for filePath in filesToAnalyze:
		print '\t' + filePath