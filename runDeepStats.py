import yaml
import fileUtils
from loadConfig import loadConfig

cfg = loadConfig()
courseDataDir = cfg['dataLoc']['courseDataDir']
courseDataExt = cfg['dataLoc']['courseDataExt']

filesToAnalyze = fileUtils.getAllFiles(dataDir = courseDataDir, dataExt = courseDataExt, latestFirst = False)
print filesToAnalyze