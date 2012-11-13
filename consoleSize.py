#!/usr/bin/python

# this code is from http://stackoverflow.com/a/943921

import os

def consoleSize():
	rows, columns = os.popen('stty size', 'r').read().split()
	return [columns, rows]