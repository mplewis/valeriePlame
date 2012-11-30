#!/usr/bin/python

import cPickle
import glob
from loadConfig import loadConfig
from jinja2 import Environment

def getSubjectsWithSvgFiles():
	cfg = loadConfig()
	directory = cfg['dataLoc']['svgDir']
	extension = 'svg'

	subjListLoc = cfg['dataLoc']['subjList']
	with open(subjListLoc, 'r') as subjData:
		fullSubjList = cPickle.load(subjData)

	subjList = []
	fileList = glob.glob(directory + '/' + '*.' + extension)
	for fileName in fileList:
		fnSplit = fileName.split('/')
		fnDotted = fnSplit[len(fnSplit) - 1]
		fnDSplit = fnDotted.split('.')
		fnClean = fnDSplit[0]
		subjList.append(fnClean)
	
	intersectList = [val for val in subjList if val in fullSubjList]
	intersectList.sort()

	return intersectList

def getSubjTriples():
	env = Environment()
	subjList = getSubjectsWithSvgFiles()

	# break the list of subjects up into triples
	# each subject chart will be displayed 4 cols wide
	# 960.gs provides 12 cols, so 3 subj charts/row
	subjListTriples = []
	counter = 0
	subjListTriple = []
	for subj in subjList:
		counter += 1
		subjListTriple.append(subj)
		if counter == 3:
			subjListTriples.append(subjListTriple)
			subjListTriple = []
			counter = 0
	if subjListTriple != []:
		while len(subjListTriple) < 3:
			# stuff list triple with Jinja2 undefined objects
			# template-side code will handle this logic
			subjListTriple.append(env.undefined())
		subjListTriples.append(subjListTriple)

	return subjListTriples

if __name__ == '__main__':
	print 'List of subjects with SVG files:'
	print getSubjectsWithSvgFiles()